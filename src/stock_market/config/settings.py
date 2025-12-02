from typing import Optional
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    currencies: list[str] = Field([], validation_alias='c')
    tickers: list[str] = Field([], validation_alias='t')

    start_date: Optional[str] = Field(None, validation_alias='s')
    end_date: Optional[str] = Field(None, validation_alias='e')

    plot: Optional[bool] = Field(False, validation_alias='p')


    csv_directory: Optional[str] = Field(None)
    ibkr_directory: Optional[str] = Field(None)
    tasty_directory: Optional[str] = Field(None)

    skip_actions: list[str] = Field([], validation_alias="a")

    last: Optional[int] = Field(None)

    do_dividends: bool = Field(False, validation_alias="div")
    do_options: bool = Field(False, validation_alias="opt")

    ibkr: bool = Field(False)
    tasty: bool = Field(False)

    new: Optional[str] = Field(None)
    table_yoy: bool = Field(False)
    plot_yoy: bool = Field(False)
    bar: bool = Field(True)


    daily: bool = Field(False, validation_alias='d')
    monthly: bool = Field(False, validation_alias='m')
    quarterly: bool = Field(False, validation_alias='q')
    yearly: bool = Field(False, validation_alias='y')
    total: bool = Field(False)

    @model_validator(mode='after')
    def check_mutually_exclusive_frequency(self):
        freqs = ['daily', 'monthly', 'quarterly', 'yearly', 'total']
        selected = [f for f in freqs if getattr(self, f)]
        if len(selected) > 1:
            raise ValueError(
                f'At most one of {freqs} may be selected. Got: {selected}'
            )

        if len(selected) == 0:
            self.monthly = True

        return self

    @property
    def period(self) -> str:
        for p in ['daily', 'monthly', 'quarterly', 'yearly', 'total']:
            if getattr(self, p):
                return p
        raise ValueError("No period selected")


    model_config = SettingsConfigDict(
        cli_parse_args=True,
        cli_implicit_flags=True,
        cli_kebab_case=True,
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore"
    )
