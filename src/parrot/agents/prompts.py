from parrot.prompts.prompt_loader import load_prompt

DEFAULT_OUTPUT_FORMAT = '{"answer": "<string>"}'


def get_sql_system_prompt(
    columns: str, output_format: str = DEFAULT_OUTPUT_FORMAT
) -> str:
    return load_prompt(
        "sql.md",
        {
            "COLUMNS": columns,
            "OUTPUT_FORMAT": output_format,
        },
        strict=True,
    )


def get_duckdb_system_prompt(
    columns: str, output_format: str = DEFAULT_OUTPUT_FORMAT
) -> str:
    return load_prompt(
        "duckdb.md",
        {
            "COLUMNS": columns,
            "OUTPUT_FORMAT": output_format,
        },
        strict=True,
    )
