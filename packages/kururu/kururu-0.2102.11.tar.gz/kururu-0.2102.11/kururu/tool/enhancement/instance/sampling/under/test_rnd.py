#  Copyright (c) 2020. Davi Pereira dos Santos
#  This file is part of the kururu project.
#  Please respect the license - more about this in the section (*) below.
#
#  kururu is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  kururu is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with kururu.  If not, see <http://www.gnu.org/licenses/>.
#
#  (*) Removing authorship by any means, e.g. by distribution of derived
#  works or verbatim, obfuscated, compiled or rewritten versions of any
#  part of this work is a crime and is unethical regarding the effort and
#  time spent here.
#  Relevant employers or funding agencies will be notified accordingly.
#

from unittest import TestCase

from aiuna.content.root import Root
from aiuna.step.dataset import Dataset

from kururu.tool.dataflow.autoins import AutoIns
from kururu.tool.enhancement.instance.sampling.over.rnd import ROS_
from kururu.tool.enhancement.instance.sampling.under.rnd import RUS_, RUS


class Test(TestCase):
    def test__rus_(self):
        augmented_iris = Root >> (Dataset() * ROS_(strategy={"virginica": 100, "versicolor": 50, "setosa": 50}))
        self.assertEqual(150, len((augmented_iris >> RUS_).X))

    def test__rus(self):
        augmented_iris =  Root >> (Dataset() * ROS_(strategy={"virginica": 100, "versicolor": 50, "setosa": 50}))
        self.assertEqual(200, len((augmented_iris >> AutoIns * RUS).X))  # TODO: inhibit UserWarning
        self.assertEqual(150, len((augmented_iris >> AutoIns * RUS).inner.X))
