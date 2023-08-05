# MIT License
#
# Copyright (c) 2020 Gabriel Nogueira (Talendar)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

""" Exposes the core functionalities of :mod:`gym_utils`.
"""

# Modules imports:
from nevopy.utils.gym_utils import callbacks
from nevopy.utils.gym_utils import fitness_function
from nevopy.utils.gym_utils import renderers

# Callbacks:
from nevopy.utils.gym_utils.callbacks import BatchObsGymCallback
from nevopy.utils.gym_utils.callbacks import GymCallback

# Fitness function
from nevopy.utils.gym_utils.fitness_function import GymFitnessFunction

# Renderers:
from nevopy.utils.gym_utils.renderers import GymRenderer
from nevopy.utils.gym_utils.renderers import NeatActivationsGymRenderer
