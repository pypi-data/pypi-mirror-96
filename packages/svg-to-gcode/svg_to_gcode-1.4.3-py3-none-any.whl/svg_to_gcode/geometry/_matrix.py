from svg_to_gcode.geometry import Vector


class Matrix:
    """The Matrix class represents matrices. It's mostly used for applying linear transformations to vectors."""
    __slots__ = 'number_of_rows', 'number_of_columns', 'matrix_list'

    def __init__(self, matrix_list):
        """
        :param matrix_list: the matrix represented as a list of rows.
        :type matrix_list: list[list]
        """
        self.number_of_rows = len(matrix_list)
        self.number_of_columns = len(matrix_list[0])

        if not all([len(row) == self.number_of_columns for row in matrix_list]):
            raise ValueError("Not a matrix. Rows in matrix_list have different lengths.")

        if not all([all([isinstance(value, float) or isinstance(value, int) for value in row]) for row in matrix_list]):
            raise ValueError("Not a matrix. matrix_list contains non numeric values.")

        self.matrix_list = matrix_list

    def __repr__(self):
        matrix_str = "\n       ".join([str(row) for row in self.matrix_list])
        return f"Matrix({matrix_str})"

    def __mul__(self, other):
        if isinstance(other, Vector):
            return self.multiply_vector(other)

        if isinstance(other, Matrix):
            return self.multiply_matrix(other)

        raise TypeError(f"can't multiply matrix by type '{type(other)}'")

    def multiply_vector(self, other_vector: Vector):
        if self.number_of_columns != 2:
            raise ValueError(f"can't multiply matrix with 2D vector. The matrix must have 2 columns, not "
                             f"{self.number_of_columns}")

        x = sum([self.matrix_list[0][k] * other_vector.x for k in range(self.number_of_columns)])
        y = sum([self.matrix_list[1][k] * other_vector.y for k in range(self.number_of_columns)])

        return Vector(x, y)

    def multiply_matrix(self, other_matrix: "Matrix"):
        if self.number_of_columns != other_matrix.number_of_rows:
            raise ValueError(f"can't multiply matrices. The first matrix must have the same number of columns as the "
                             f"second has rows. {self.number_of_columns}!={other_matrix.number_of_rows}")

        matrix_list = [[
                    sum([self.matrix_list[i][k] * other_matrix.matrix_list[k][j] for k in range(self.number_of_columns)])
                for j in range(other_matrix.number_of_columns)]
            for i in range(self.number_of_rows)]

        return Matrix(matrix_list)


class IdentityMatrix(Matrix):
    def __init__(self, size):
        matrix_list = [[int(i == j) for j in range(size)] for i in range(size)]
        super().__init__(matrix_list)
