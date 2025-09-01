import pandas as pd
import glob
import os

path = "data"

arquivos = glob.glob(os.path.join(path, "bolsas_usp_*.csv"))

dfs = []

for arquivo in arquivos:
    df = pd.read_csv(arquivo)
    
    # garante que "Total de Bolsa" é numérico
    df["Total de Bolsa"] = pd.to_numeric(df["Total de Bolsa"], errors="coerce").fillna(0).astype(int)
    
    # adiciona no consolidado
    dfs.append(df)

df_all = pd.concat(dfs, ignore_index=True)


# 1. Total de bolsas por ano
total_por_ano = df_all.groupby("Edital")["Total de Bolsa"].sum().reset_index()

# 2. Total de bolsas por vertente (para cada ano)
total_por_vertente = df_all.groupby(["Edital", "Vertente"])["Total de Bolsa"].sum().reset_index()

# 3. Total de bolsas por unidade (para cada ano)
total_por_unidade = df_all.groupby(["Edital", "Unidade", "Vertente"])["Total de Bolsa"].sum().reset_index()

# 4. Total de bolsas por orientador (para cada ano)
total_por_orientador = df_all.groupby(["Edital", "Orientador"])["Total de Bolsa"].sum().reset_index()

saida = "analise_bolsas"

os.makedirs(saida, exist_ok=True)

total_por_ano.to_csv(os.path.join(saida, "total_por_ano.csv"), index=False)
total_por_vertente.to_csv(os.path.join(saida, "total_por_vertente.csv"), index=False)
total_por_unidade.to_csv(os.path.join(saida, "total_por_unidade.csv"), index=False)
total_por_orientador.to_csv(os.path.join(saida, "total_por_orientador.csv"), index=False)

print("✅ Arquivos de análise salvos na pasta:", saida)

