# Tokenizer exceptions
UNEXPECTED_CHARACTER = 'Unexpected character.'
RESERVED_KEYWORD = "Reserved keyword '%s'."
INVALID_HEX_STRING = "Invalid hex string '%s'."
MULTILINE_STRINGS_NOT_SUPPORTED = 'Unterminated single-line string.'
EOF_DURING_STRING = 'EOF reached during string.'
UNEXPECTED_EOF = 'Unexpected EOF.'
NUMBER_NOT_ZERO = "Number cannot start with '0'."
ALTERNATE_BASE_FLOAT = 'Cannot have alternate bases on floats.'
UNDERSCORE_ENDED_NUMBER = "Cannot end number literal with '_'."
INVALID_ESCAPE = "Invalid escape character '%s'."

# Parser exceptions
INVALID_ASSIGNMENT = 'Invalid assignment target.'
ITERATION_INVALID_ASSIGNMENT = 'Invalid assignment target for iteration.'
EXPECT_EXPRESSOIN = 'Expect expression.'
INVALID_ASYNC = "Async keyword not supported with '%s' statements."
INVALID_ASYNC_EXPR = 'Async keyword not supported with expression statements.'
INVALID_ASYNC_FOR = "Async for loops only compatible with iteration (using ':' syntax)."
EXPECT_PROPERTY_NAME = "Expect property name after '.'."
