import unittest
from typing import Union


def get_number_arg(message: str) -> Union[int, None]:
    value_to_return = None
    list_of_args = message.split(' ')
    if len(list_of_args) > 1:
        try:
            value_to_return = int(list_of_args[1])
            return value_to_return
        except ValueError:
            return value_to_return


class GetSecondArgInt(unittest.TestCase):

    def test_failure_not_int(self):
        self.assertIsNone(get_number_arg('#command not_int'))

    def test_failure_no_arg(self):
        self.assertIsNone(get_number_arg('#command'))

    def test_success_is_int(self):
        self.assertEqual(get_number_arg('#command 500'), 500)


if __name__ == '__main__':
    unittest.main()
