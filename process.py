from multiprocessing import Semaphore, Process
from pathlib import Path

import matplotlib
import pandas as pd
import requests


def main():
    url = "https://ftp.ibge.gov.br/Projecao_da_Populacao/Projecao_da_Populacao_2024/projecoes_2024_tab2_grupo_quinquenal.xlsx"
    dest_dir = Path("data")
    if not dest_dir.exists():
        dest_dir.mkdir()
    dest_file = dest_dir / "projecoes_2024_tab2_grupo_quinquenal.xlsx"
    if not dest_file.exists():
        with open(dest_file, "wb") as f:
            f.write(requests.get(url).content)

    df = pd.read_excel(
        dest_file,
        sheet_name="2) POP_GRUPO QUINQUENAL",
        skiprows=5,
    )

    dados = (
        df.melt(
            id_vars=["GRUPO ETÁRIO", "SEXO", "CÓD.", "SIGLA", "LOCAL"],
            var_name="ANO",
            value_name="POPULAÇÃO",
        )
        .drop(columns=["CÓD."])
        .assign(
            **{
                "GRUPO ETÁRIO": lambda x: x["GRUPO ETÁRIO"].str.strip(),
                "ANO": lambda x: pd.to_datetime(x["ANO"], format="%Y"),
            }
        )
    )

    _faixa = [
        "00-04",
        "05-09",
        "10-14",
        "15-19",
        "20-24",
        "25-29",
        "30-34",
        "35-39",
        "40-44",
        "45-49",
        "50-54",
        "55-59",
        "60-64",
        "65-69",
        "70-74",
        "75-79",
        "80-84",
        "85-89",
        "90+",
    ]
    _idade = [(2 * i + 5) / 2 for i in range(0, 90, 5)] + [92.5]
    idade = pd.DataFrame({"GRUPO ETÁRIO": _faixa, "idade": _idade})

    dados2 = dados.merge(idade, how="left")

    data = dados2[dados2["LOCAL"] == "Brasil"]

    data_br = (
        dados2[dados2["LOCAL"] == "Brasil"]
        .drop(columns=["LOCAL", "SIGLA"])
        .query("SEXO != 'Ambos'")
    )

    data_br_homens = data_br.query("SEXO == 'Homens'").pivot_table(
        index=["ANO"],
        columns="GRUPO ETÁRIO",
        values="POPULAÇÃO",
        aggfunc="sum",
    )
    data_br_mulheres = data_br.query("SEXO == 'Mulheres'").pivot_table(
        index=["ANO"],
        columns="GRUPO ETÁRIO",
        values="POPULAÇÃO",
        aggfunc="sum",
    )
    years = pd.date_range(start="2000-01-01", end="2070-01-01", freq="D")
    data_br_homens = (
        data_br_homens.reindex(years)
        .interpolate(method="time")
        .resample("ME")
        .mean()
        .stack()
        .reset_index()
        .rename(columns={"level_0": "ANO", 0: "POPULAÇÃO"})
        .assign(SEXO="Homens")
    )
    data_br_mulheres = (
        data_br_mulheres.reindex(years)
        .interpolate(method="spline", order=3)
        .resample("ME")
        .mean()
        .stack()
        .reset_index()
        .rename(columns={"level_0": "ANO", 0: "POPULAÇÃO"})
        .assign(SEXO="Mulheres")
    )
    data_br_interpol = pd.concat([data_br_homens, data_br_mulheres]).merge(
        idade, how="left"
    )

    data_br_interpol.to_csv(dest_dir / "data.csv", index=False)


if __name__ == "__main__":
    main()
