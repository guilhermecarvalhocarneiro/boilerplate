class ParserContent:
    """Class responsible for parsing the content of the snippets for the final files
    with the interpolation of the variables with the attributes of the model"""

    def __init__(self, keys: list, contents: list, snippet: str):
        super().__init__()
        self.snippet = snippet
        self.keys = keys
        self.contents = contents

    def replace(self) -> str:
        """Method to replace the snippet keys by the content..

        Returns:
            str: Content to be saved in the definitive class / model file.

        Raises:
            When the values of keys and contents have different sizes.
            When any value of keys contents or snippet is not informed.
        """
        try:
            if len(self.keys) == 0 or len(self.contents) == 0 or len(self.snippet.strip()) == 0:
                raise Exception(
                    "It is necessary to inform the keys, contents and snippet values, and they cannot be white."
                )
            if len(self.keys) != len(self.contents):
                raise Exception("Size of keys and contents attributes must be the same.")
            for index, key in enumerate(self.keys):
                self.snippet = self.snippet.replace(key, self.contents[index])
            return self.snippet.strip()
        except Exception as error:
            return f"\nError occurred: \n    {error}.\n"

