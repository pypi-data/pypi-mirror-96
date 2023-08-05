from __future__ import division

import numpy as np
from .fourier_transform import FourierTransform, multiplex_for_tensor_fields, _get_float_and_complex_dtype
from ..field import Field, CartesianGrid, RegularCoords
from ..config import Configuration
import numexpr as ne

try:
	import mkl_fft._numpy_fft as _fft_module
except ImportError:
	_fft_module = np.fft

def make_fft_grid(input_grid, q=1, fov=1):
	'''Calculate the grid returned by a Fast Fourier Transform.

	Parameters
	----------
	input_grid : Grid
		The grid defining the sampling in the real domain..
	q : scalar
		The amount of zeropadding to perform. A value of 1 denotes no zeropadding.
	fov : scalar
		The amount of cropping to perform in the Fourier domain.

	Returns
	-------
	Grid
		The grid defining the sampling in the Fourier domain.
	'''
	q = np.ones(input_grid.ndim, dtype='float') * q
	fov = np.ones(input_grid.ndim, dtype='float') * fov

	# Check assumptions
	if not input_grid.is_regular:
		raise ValueError('The input_grid must be regular.')
	if not input_grid.is_('cartesian'):
		raise ValueError('The input_grid must be cartesian.')

	delta = (2 * np.pi / (input_grid.delta * input_grid.dims)) / q
	dims = (input_grid.dims * fov * q).astype('int')
	zero = delta * (-dims / 2 + np.mod(dims, 2) * 0.5)

	return CartesianGrid(RegularCoords(delta, dims, zero))

def _numexpr_grid_shift(shift, grid, out=None):
	'''Fast evaluation of np.exp(1j * np.dot(shift, grid.coords)) using NumExpr.

	Parameters
	----------
	shift : array_like
		The coordinates of the shift.
	grid : Grid
		The grid on which to calculate the shift.
	out : array_like
		An existing array where the outcome is going to be stored. This must
		have the correct shape and dtype. No checking will be performed. If
		this is None, a new array will be allocated and returned.

	Returns
	-------
	array_like
		The calculated complex shift array.
	'''
	variables = {}
	command = []
	coords = grid.coords

	for i in range(grid.ndim):
		variables['a%d' % i] = shift[i]
		variables['b%d' % i] = coords[i]

		command.append('a%d * b%d' % (i,i))

	command = 'exp(1j * (' + '+'.join(command) + '))'
	return ne.evaluate(command, local_dict=variables, out=out)

class FastFourierTransform(FourierTransform):
	'''A Fast Fourier Transform (FFT) object.

	This Fourier transform calculates FFTs with zeropadding and cropping. This
	Fourier transform requires the input grid to be regular in Cartesian coordinates. Every
	number of dimensions is allowed.

	Parameters
	----------
	input_grid : Grid
		The grid that is expected for the input field.
	q : scalar
		The amount of zeropadding to perform. A value of 1 denotes no zeropadding.
	fov : scalar
		The amount of cropping to perform in the Fourier domain.
	shift : array_like or scalar
		The amount by which to shift the output grid.
	emulate_fftshifts : boolean or None
		Whether to emulate FFTshifts normally used in the FFT by multiplications in the
		opposite domain. Enabling this increases performance by 3x, but degrades accuracy of
		the FFT by 10x. If this is None, the choice will be determined by the configuration
		file.

	Raises
	------
	ValueError
		If the input grid is not regular or Cartesian.
	'''
	def __init__(self, input_grid, q=1, fov=1, shift=0, emulate_fftshifts=None):
		# Check assumptions
		if not input_grid.is_regular:
			raise ValueError('The input_grid must be regular.')
		if not input_grid.is_('cartesian'):
			raise ValueError('The input_grid must be Cartesian.')

		self.input_grid = input_grid

		self.shape_in = input_grid.shape
		self.weights = input_grid.weights
		self.size = input_grid.size
		self.ndim = input_grid.ndim

		# Get the value from the configuration file if left at the default.
		if emulate_fftshifts is None:
			emulate_fftshifts = Configuration().fourier.fft.emulate_fftshifts
		self.emulate_fftshifts = emulate_fftshifts

		self.output_grid = make_fft_grid(input_grid, q, fov).shifted(shift)
		self.internal_grid = make_fft_grid(input_grid, q, 1)

		self.shape_out = self.output_grid.shape
		self.internal_shape = (self.shape_in * q).astype('int')
		self.internal_array = np.zeros(self.internal_shape, 'complex')

		# Calculate the part of the array in which to insert the input field (for zeropadding).
		if np.allclose(self.internal_shape, self.shape_in):
			self.cutout_input = None
		else:
			cutout_start = (self.internal_shape / 2.).astype('int') - (self.shape_in / 2.).astype('int')
			cutout_end = cutout_start + self.shape_in
			self.cutout_input = tuple([slice(start, end) for start, end in zip(cutout_start, cutout_end)])

		# Calculate the part of the array to extract the output field (for cropping).
		if np.allclose(self.internal_shape, self.shape_out):
			self.cutout_output = None
		else:
			cutout_start = (self.internal_shape / 2.).astype('int') - (self.shape_out / 2.).astype('int')
			cutout_end = cutout_start + self.shape_out
			self.cutout_output = tuple([slice(start, end) for start, end in zip(cutout_start, cutout_end)])

		# Calculate the shift array when the input grid was shifted compared to the native shift
		# expected by the numpy FFT implementation.
		center = input_grid.zero + input_grid.delta * (np.array(input_grid.dims) // 2)
		self.shift_input = _numexpr_grid_shift(-center, self.output_grid)

		# Remove piston shift (remove central shift phase)
		self.shift_input /= np.fft.ifftshift(self.shift_input.reshape(self.shape_out)).ravel()[0]

		# Calculate the multiplication for emulating the FFTshift (if requested).
		if emulate_fftshifts:
			f_shift = input_grid.delta * np.array(self.internal_shape[::-1] // 2)
			fftshift = _numexpr_grid_shift(f_shift, self.internal_grid)

			if self.cutout_output:
				self.shift_input *= fftshift.reshape(self.internal_shape)[self.cutout_output].ravel()
			else:
				self.shift_input *= fftshift

		# Apply weights for Fourier normalization.
		self.shift_input *= self.weights

		# Calculate the shift array when the output grid was shifted compared to the native shift
		# expcted by the numpy FFT implementation.
		shift = np.ones(self.input_grid.ndim) * shift
		if np.allclose(shift, 0):
			self.shift_output = 1
		else:
			self.shift_output = _numexpr_grid_shift(-shift, self.input_grid)

		# Calculate the multiplication for emulating the FFTshift (if requested).
		if emulate_fftshifts:
			f_shift = self.input_grid.delta * np.array(self.internal_shape[::-1] // 2)
			fftshift = _numexpr_grid_shift(f_shift, self.internal_grid)

			fftshift *= np.exp(-1j * np.dot(f_shift, self.internal_grid.zero))

			if self.cutout_input:
				self.shift_output *= fftshift.reshape(self.internal_shape)[self.cutout_input].ravel()
			else:
				self.shift_output *= fftshift

		# Detect if we don't need to shift in the output plane (to avoid a multiplication in the operation).
		if np.isscalar(self.shift_output) and np.allclose(self.shift_output, 1):
			self.shift_output = None

	@multiplex_for_tensor_fields
	def forward(self, field):
		'''Returns the forward Fourier transform of the :class:`Field` field.

		Parameters
		----------
		field : Field
			The field to Fourier transform.

		Returns
		-------
		Field
			The Fourier transform of the field.
		'''
		if self.cutout_input is None:
			self.internal_array[:] = field.reshape(self.shape_in)

			if self.shift_output is not None:
				self.internal_array *= self.shift_output.reshape(self.shape_in)
		else:
			self.internal_array[:] = 0
			self.internal_array[self.cutout_input] = field.reshape(self.shape_in)

			if self.shift_output is not None:
				self.internal_array[self.cutout_input] *= self.shift_output.reshape(self.shape_in)

		if not self.emulate_fftshifts:
			self.internal_array = np.fft.ifftshift(self.internal_array)

		fft_array = _fft_module.fftn(self.internal_array)

		if not self.emulate_fftshifts:
			fft_array = np.fft.fftshift(fft_array)

		if self.cutout_output is None:
			res = fft_array.ravel()
		else:
			res = fft_array[self.cutout_output].ravel()

		res *= self.shift_input

		float_dtype, complex_dtype = _get_float_and_complex_dtype(field.dtype)
		return Field(res, self.output_grid).astype(complex_dtype, copy=False)

	@multiplex_for_tensor_fields
	def backward(self, field):
		'''Returns the inverse Fourier transform of the :class:`Field` field.

		Parameters
		----------
		field : Field
			The field to inverse Fourier transform.

		Returns
		-------
		Field
			The inverse Fourier transform of the field.
		'''
		if self.cutout_output is None:
			self.internal_array[:] = field.reshape(self.shape_out)
			self.internal_array /= self.shift_input.reshape(self.shape_out)
		else:
			self.internal_array[:] = 0
			self.internal_array[self.cutout_output] = field.reshape(self.shape_out)
			self.internal_array[self.cutout_output] /= self.shift_input.reshape(self.shape_out)

		if not self.emulate_fftshifts:
			self.internal_array = np.fft.ifftshift(self.internal_array)

		fft_array = _fft_module.ifftn(self.internal_array)

		if not self.emulate_fftshifts:
			fft_array = np.fft.fftshift(fft_array)

		if self.cutout_input is None:
			res = fft_array.ravel()
		else:
			res = fft_array[self.cutout_input].ravel()

		if self.shift_output is not None:
				res /= self.shift_output

		float_dtype, complex_dtype = _get_float_and_complex_dtype(field.dtype)
		return Field(res, self.input_grid).astype(complex_dtype, copy=False)
