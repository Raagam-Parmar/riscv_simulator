class Field:
    """
    A class to define a bit field within an integer
    """

    def __init__(self, hi: int, lo: int):
        """
        Constructs a field object

        :param hi: Highest bit index (inclusive)
        :param lo: Lowest bit index (inclusive)
        """

        self.hi = hi
        self.lo = lo

        w = hi - lo + 1
        self.width: int = w
        self.mask: int = (1 << w) - 1

    def extract(self, data: int) -> int:
        """
        Extract the field from a given integer

        :param data: An integer from which the field's value is to be extracted

        :return: The value of the field extracted from the given integer
        """

        return (data >> self.lo) & self.mask

    def __repr__(self):
        """
        `Field (hi...lo)`
        """

        return f"Field({self.hi}...{self.lo})"
