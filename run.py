import sys
import shutil
from multiprocessing import Pool
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


sns.set_style("whitegrid")
font = {"family": "Times New Roman", "weight": "normal", "size": 20}
matplotlib.rc("font", **font)


def formatter_x(x, p):
    if x == 0:
        return "0"
    else:
        return f"{abs(x)/10**6:.0f} mi"


def formatter_y(x, p):
    if x < 90:
        return f"{x-2.5: >2.0f}-{x+1.5: <2.0f}"
    else:
        return "90+"


def plot_pop_pyramid(data, date):
    dh = data.loc[(data["SEXO"] == "Homens") & (data["ANO"] == date)]
    dm = data.loc[(data["SEXO"] == "Mulheres") & (data["ANO"] == date)]
    f, ax = plt.subplots()
    f.set_size_inches(16, 16)
    h = ax.barh(
        dh["idade"],
        dh["POPULAÇÃO"],
        height=4.9,
        color=(0.6, 0.25, 0.25),
        label="Homens",
    )
    m = ax.barh(
        dm["idade"],
        dm["POPULAÇÃO"] * -1,
        height=4.9,
        color=(0.25, 0.25, 0.6),
        label="Mulheres",
    )
    f.suptitle(
        "Projeção da População Brasileira\npor Idade e Sexo (2000-2070)",
        fontfamily="Georgia",
        fontsize=56,
        fontweight="bold",
        horizontalalignment="left",
        x=0.025,
        y=0.975,
    )
    total_pop = data.loc[data["ANO"] == date, "POPULAÇÃO"].sum()
    ax.set_title(f"População total: {int(total_pop):,}".replace(",", "."), fontsize=22)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(formatter_x))
    ax.set_yticks(np.arange(2.5, 95, 5))
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(formatter_y))
    for t in ax.get_yticklabels():
        t.set_fontname("monospace")
    ax.set_xlim(-9.5 * 10**6, 9.5 * 10**6)
    ax.set_ylim(bottom=-1, top=96)
    ax.legend(handles=[h, m], loc="upper right")
    ax.grid(False)
    ax.text(0, 25, date.year, size=300, alpha=0.3, horizontalalignment="center")
    ax.set_position([0.08, 0.12, 0.89, 0.7])  # [left, bottom, width, height]
    plt.figtext(
        x=0.025, y=0.025, s="Fonte: IBGE/Projeções da População (2024)", fontsize=18
    )
    plt.figtext(
        x=0.975,
        y=0.025,
        s="Autor: Daniel Komesu",
        fontsize=18,
        horizontalalignment="right",
    )
    return f, ax


def plot(data, date, x, dest_plots_dir):
    dest_plot_filepath = dest_plots_dir / f"{x:05}.png"
    # if dest_plot_filepath.exists():
    #     return
    f, ax = plot_pop_pyramid(data, date)
    plt.savefig(dest_plot_filepath, dpi=300)
    plt.close()
    sys.stdout.write(f"Saved {dest_plot_filepath}\n")
    sys.stdout.flush()


def main():

    dest_plots_dir = Path("plots")
    dest_plots_dir.mkdir(parents=True, exist_ok=True)

    data = pd.read_csv("data/data.csv", parse_dates=["ANO"])

    dates = pd.date_range(start="2000-01", end="2070-02", freq="ME")
    n_frames = len(dates)

    with Pool(16) as p:
        p.starmap(
            plot, [(data, date, x, dest_plots_dir) for x, date in enumerate(dates)]
        )

    last_plot_filepath = dest_plots_dir / f"{n_frames-1:05}.png"
    for i in range(120):
        print(f"Copying {last_plot_filepath} to {n_frames+i:05}.png")
        shutil.copy(last_plot_filepath, dest_plots_dir / f"{n_frames+i:05}.png")

    print("All done!")


if __name__ == "__main__":
    main()
