from __future__ import division
import functools

import numpy as np
from ..field import Field, CartesianGrid, UnstructuredCoords, make_hexagonal_grid

def circular_aperture(diameter, center=None):
	'''Makes a Field generator for a circular aperture.

	Parameters
	----------
	diameter : scalar
		The diameter of the aperture.
	center : array_like
		The center of the aperture

	Returns
	-------
	Field generator
		This function can be evaluated on a grid to get a Field.
	'''
	if center is None:
		shift = np.zeros(2)
	else:
		shift = center * np.ones(2)

	def func(grid):
		if grid.is_('cartesian'):
			if grid.is_separated:
				x, y = grid.separated_coords
				f = ((((x - shift[0])**2)[np.newaxis, :] + ((y - shift[1])**2)[:, np.newaxis]) <= (diameter / 2)**2).ravel()
			else:
				x, y = grid.coords
				f = ((x - shift[0])**2 + (y - shift[1])**2) <= (diameter / 2)**2
		else:
			f = grid.r <= (diameter / 2)

		return Field(f.astype('float'), grid)

	return func

def elliptical_aperture(diameters, center=None):
	'''Makes a Field generator for an elliptical aperture.

	Parameters
	----------
	diameters : array_like
		The diameters of the aperture in the two directions.
	center : array_like or None
		The center of the aperture.

	Returns
	-------
	Field generator
		This function can be evaluated on a grid to get a Field.
	'''
	if center is None:
		shift = np.zeros(2)
	else:
		shift = center * np.ones(2)

	def func(grid):
		if grid.is_separated:
			x, y = grid.separated_coords
			f = ((((x - shift[0]) / (diameters[0] / 2))**2)[np.newaxis, :] + (((y - shift[1]) / (diameters[1] / 2))**2)[:, np.newaxis] <= 1).ravel()
		else:
			x, y = grid.as_('cartesian').coords
			f = (((x - shift[0]) / (diameters[0] / 2))**2 + ((y - shift[1]) / (diameters[1] / 2))**2) <= 1

		return Field(f.astype('float'), grid)

	return func

def rectangular_aperture(size, center=None):
	'''Makes a Field generator for a rectangular aperture.

	Parameters
	----------
	size : scalar or array_like
		The length of the sides. If this is scalar, a square aperture is assumed.
	center : array_like
		The center of the aperture

	Returns
	-------
	Field generator
		This function can be evaluated on a grid to get a Field.
	'''
	dim = size * np.ones(2)

	if center is None:
		shift = np.zeros(2)
	else:
		shift = center * np.ones(2)

	def func(grid):
		if grid.is_('cartesian') and grid.is_separated:
			x, y = grid.separated_coords
			f = ((np.abs(x - shift[0]) <= (dim[0] / 2))[np.newaxis, :] * (np.abs(y - shift[1]) <= (dim[1] / 2))[:, np.newaxis]).ravel()
		else:
			x, y = grid.as_('cartesian').coords
			f = (np.abs(x - shift[0]) <= (dim[0] / 2)) * (np.abs(y - shift[1]) <= (dim[1] / 2))

		return Field(f.astype('float'), grid)

	return func

def regular_polygon_aperture(num_sides, circum_diameter, angle=0, center=None):
	'''Makes a Field generator for a regular-polygon-shaped aperture.

	Parameters
	----------
	num_sides : integer
		The number of sides for the polygon.
	circum_diameter : scalar
		The circumdiameter of the polygon.
	angle : scalar
		The angle by which to turn the polygon.
	center : array_like
		The center of the aperture

	Returns
	-------
	Field generator
		This function can be evaluated on a grid to get a Field.
	'''
	if num_sides < 3:
		raise ValueError('The number of sides for a regular polygon has to greater or equal to 3.')

	if center is None:
		shift = np.zeros(2)
	else:
		shift = center * np.ones(2)

	epsilon = 1e-6

	apothem = np.cos(np.pi / num_sides) * circum_diameter / 2
	apothem += apothem * epsilon

	if center is None:
		shift = np.zeros(2)
	else:
		shift = center * np.ones(2)

	# Make use of symmetry
	if num_sides % 2 == 0:
		thetas = np.arange(int(num_sides / 2), dtype='float') * np.pi / int(num_sides / 2) + angle
	else:
		thetas = np.arange(int(num_sides / 2) + 1) * (num_sides - 2) * np.pi / (num_sides / 2) + angle

	mask = rectangular_aperture(circum_diameter)

	def func(grid):
		g = grid.as_('cartesian')

		if g.is_separated:
			x, y = g.separated_coords

			x = x - shift[0]
			y = y - shift[1]

			ind_x = np.flatnonzero(x**2 < ((circum_diameter / 2)**2))
			if not len(ind_x):
				return grid.zeros()

			ind_y = np.flatnonzero(y**2 < ((circum_diameter / 2)**2))
			if not len(ind_y):
				return grid.zeros()

			m_x = slice(ind_x[0], ind_x[-1] + 1)
			m_y = slice(ind_y[0], ind_y[-1] + 1)

			x = x[m_x]
			y = y[m_y]

			f_sub = np.ones((len(ind_y), len(ind_x)))

			if num_sides % 2 == 0:
				for theta in thetas:
					f_sub *= ((np.cos(theta) * x)[np.newaxis, :] + (np.sin(theta) * y)[:, np.newaxis])**2 <= apothem**2
			else:
				for theta in thetas:
					f_sub *= (np.abs(np.sin(theta) * x)[np.newaxis, :] - (np.cos(theta) * y)[:, np.newaxis]) <= apothem

			f = np.zeros(g.shape)
			f[m_y, m_x] = f_sub

			return Field(f.ravel(), grid)

		# Slow backup method
		f = np.ones(grid.size, dtype='float')
		m = mask(g) != 0

		x, y = g.coords
		x = x[m] - shift[0]
		y = y[m] - shift[1]

		f[~m] = 0

		# Make use of symmetry
		if num_sides % 2 == 0:
			for theta in thetas:
				f[m] *= (np.cos(theta) * x + np.sin(theta) * y)**2 <= apothem**2
		else:
			for theta in thetas:
				f[m] *= (np.abs(np.sin(theta) * x) + -np.cos(theta) * y) <= apothem

		return Field(f, grid)

	return func

# Convenience function
def hexagonal_aperture(circum_diameter, angle=0, center=None):
	'''Makes a Field generator for a hexagon aperture.

	Parameters
	----------
	circum_diameter : scalar
		The circumdiameter of the polygon.
	angle : scalar
		The angle by which to turn the hexagon.
	center : array_like
		The center of the aperture

	Returns
	-------
	Field generator
		This function can be evaluated on a grid to get a Field.
	'''
	return regular_polygon_aperture(6, circum_diameter, angle, center)

def make_spider(p1, p2, spider_width):
	'''Make a rectangular obstruction from `p1` to `p2`.

	Parameters
	----------
	p1 : list or ndarray
		The starting coordinates of the spider.
	p2 : list or ndarray
		The end coordinates of the spider.
	spider_width : scalar
		The full width of the spider.

	Returns
	-------
	Field generator
		The spider obstruction.
	'''
	delta = np.array(p2) - np.array(p1)
	shift = delta / 2 + np.array(p1)

	spider_angle = np.arctan2(delta[1], delta[0])
	spider_length = np.linalg.norm(delta)

	spider = rectangular_aperture((spider_length, spider_width))

	def func(grid):
		x, y = grid.shifted(-shift).coords

		x_new = x * np.cos(spider_angle) + y * np.sin(spider_angle)
		y_new = y * np.cos(spider_angle) - x * np.sin(spider_angle)
		spider_grid = CartesianGrid(UnstructuredCoords([x_new, y_new]))

		return 1 - spider(spider_grid)
	return func

def make_spider_infinite(p, angle, spider_width):
	'''Make an infinite spider starting at `p` and extending at an angle `angle`.

	Parameters
	----------
	p : list or ndarray
		The starting coordinate of the spider.
	angle : scalar
		The angle to which the spider is pointing in degrees.
	spider_width : scalar
		The full width of the spider.

	Returns
	-------
	Field generator
		The spider obstruction.
	'''
	spider_angle = np.radians(angle)

	def func(grid):
		x,y = grid.shifted(p).coords

		x_new = x * np.cos(spider_angle) + y * np.sin(spider_angle)
		y_new = y * np.cos(spider_angle) - x * np.sin(spider_angle)
		infinite_spider = np.logical_and(np.abs(y_new) <= (spider_width / 2), x_new >= 0)

		return Field(1 - infinite_spider, grid)
	return func

def make_obstructed_circular_aperture(pupil_diameter, central_obscuration_ratio, num_spiders=0, spider_width=0.01):
	'''Make a simple circular aperture with central obscuration and support structure.

	Parameters
	----------
	pupil_diameter : scalar
		The diameter of the circular aperture.
	central_obscuration_ratio : scalar
		The ratio of the diameter of the central obscuration compared to the pupil diameter.
	num_spiders : int
		The number of spiders holding up the central obscuration.
	spider_width : scalar
		The full width of the spiders.

	Returns
	-------
	Field generator
		The circularly obstructed aperture.
	'''
	central_obscuration_diameter = pupil_diameter * central_obscuration_ratio

	def func(grid):
		pupil_outer = circular_aperture(pupil_diameter)(grid)
		pupil_inner = circular_aperture(central_obscuration_diameter)(grid)
		spiders = 1

		spider_angles = np.linspace(0, 2*np.pi, num_spiders, endpoint=False)

		for angle in spider_angles:
			x = pupil_diameter * np.cos(angle)
			y = pupil_diameter * np.sin(angle)

			spiders *= make_spider((0, 0), (x, y), spider_width)(grid)

		return (pupil_outer - pupil_inner) * spiders
	return func

def make_obstruction(aperture):
	'''Create an obstruction of `aperture`.

	Parameters
	----------
	aperture : Field generator
		The aperture to invert.

	Returns
	-------
	Field generator
		The obstruction.
	'''
	return lambda grid: 1 - aperture(grid)

def make_rotated_aperture(aperture, angle):
	'''Create a rotated version of `aperture`.

	Parameters
	----------
	aperture : Field generator
		The aperture to rotate.
	angle : scalar
		The angle in radians by which to rotate the aperture.

	Returns
	-------
	Field generator
		The rotated aperture.
	'''
	return lambda grid: Field(aperture(grid.rotated(-angle)), grid)

def make_segmented_aperture(segment_shape, segment_positions, segment_transmissions=1, return_segments=False):
	'''Create a segmented aperture.

	Parameters
	----------
	segment_shape : Field generator
		The shape for each of the segments.
	segment_positions : Grid
		The center position for each of the segments.
	segment_transmissions : scalar or ndarray
		The transmission for each of the segments. If this is a scalar, the same transmission is used for all segments.
	return_segments : boolean
		Whether to return a ModeBasis of all segments as well.

	Returns
	-------
	Field generator
		The segmented aperture.
	list of Field generators
		The segments. Only returned if return_segments is True.
	'''
	segment_transmissions = np.ones(segment_positions.size) * segment_transmissions

	def func(grid):
		res = np.zeros(grid.size, dtype=segment_transmissions.dtype)

		for p, t in zip(segment_positions.points, segment_transmissions):
			segment = segment_shape(grid.shifted(-p))
			res[segment > 0.5] = t

		return Field(res, grid)

	if return_segments:
		def seg(grid, p, t):
			return segment_shape(grid.shifted(-p)) * t

		segments = []
		for p, t in zip(segment_positions.points, segment_transmissions):
			segments.append(functools.partial(seg, p=p, t=t))

		return func, segments
	else:
		return func

def make_hexagonal_segmented_aperture(num_rings, segment_flat_to_flat, gap_size, starting_ring=0, return_segments=False):
	'''Create a hexagonal segmented aperture.

	All segments have a flat-to-flat size of `segment_flat_to_flat`, which means that
	the segment pitch (the distance between the centers of adjacent segments) is the sum
	of the segment flat-to-flat size and the gap size.

	Parameters
	----------
	num_rings : int
		The number of rings of hexagons to include, not counting the central segment.
		So 2 for a JWST-like aperture, 3 for a Keck-like aperture, and so on.
	segment_flat_to_flat : scalar
		The distance between sides (flat-to-flat) of a single segment.
	gap_size : scalar
		The gap between adjacent segments.
	starting_ring : int
		The first ring of segments. This can be used to exclude the center segment (by
		setting it to one), or the center segment and first ring (by setting it to two).
		The default (zero) includes the center segment.
	return_segments : boolean
		Whether to return a ModeBasis of all segments as well.

	Returns
	-------
	Field generator
		The segmented aperture.
	list of Field generators
		The segments. Only returned if return_segments is True.
	'''
	segment_circum_diameter = segment_flat_to_flat * 2 / np.sqrt(3)
	segment = hexagonal_aperture(segment_circum_diameter, np.pi / 2)

	segment_pitch = segment_flat_to_flat + gap_size
	segment_positions = make_hexagonal_grid(segment_pitch, num_rings, pointy_top=False)

	if starting_ring != 0:
		starting_segment = 3 * (starting_ring - 1) * starting_ring + 1

		mask = segment_positions.zeros(dtype='bool')
		mask[starting_segment:] = True

		segment_positions = segment_positions.subset(mask)

	return make_segmented_aperture(segment, segment_positions, return_segments=return_segments)
