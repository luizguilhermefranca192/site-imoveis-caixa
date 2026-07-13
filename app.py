from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():

    # Lê o Excel
    df = pd.read_excel(
    "Lista_imoveis_geral.xlsx",
    engine="openpyxl"
    )   

    # Remove espaços dos nomes das colunas
    df.columns = [str(c).strip() for c in df.columns]

    print("\n===== COLUNAS =====")
    print(df.columns.tolist())
    print("===================\n")

    # ======================================================
    # Padroniza a coluna de endereço do mapa
    # ======================================================
    for coluna in df.columns:
        nome = coluna.strip().lower()

        if nome == "endereço mapa" or nome == "endereco mapa":
            df["Endereço Mapa"] = df[coluna].fillna("").astype(str)
            print(f'Usando coluna "{coluna}" para o Google Maps.')
            break

    if "Endereço Mapa" not in df.columns:
        if "Endereço" in df.columns:
            print("ATENÇÃO: coluna 'Endereço mapa' não encontrada. Usando 'Endereço'.")
            df["Endereço Mapa"] = df["Endereço"].fillna("").astype(str)
        elif "Endereco" in df.columns:
            df["Endereço Mapa"] = df["Endereco"].fillna("").astype(str)
        else:
            df["Endereço Mapa"] = ""

    # ======================================================
    # Link
    # ======================================================
    if "Link de acesso" in df.columns:
        df["Link"] = df["Link de acesso"].fillna("").astype(str)
    else:
        df["Link"] = ""

    def corrigir_link(x):
        x = str(x).strip()

        if x == "" or x.lower() == "nan":
            return ""

        if x.startswith("http"):
            return x

        return "https://venda-imoveis.caixa.gov.br/" + x.lstrip("/")

    df["Link"] = df["Link"].apply(corrigir_link)

    # ======================================================
    # Texto
    # ======================================================
    colunas_texto = [
        "UF",
        "Cidade",
        "Bairro",
        "Tipo Imóvel",
        "Modalidade de venda",
        "Faixa Preço",
        "Faixa Desconto",
        "Quartos",
        "Vagas"
    ]

    for col in colunas_texto:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("")
                .astype(str)
                .str.strip()
                .str.upper()
            )

    # ======================================================
    # Valores
    # ======================================================

    # -------- PREÇO --------
    if "Preço" in df.columns:
        df["Preço Num"] = pd.to_numeric(df["Preço"], errors="coerce")

        df["Preço"] = df["Preço Num"].apply(
            lambda x: f"{int(x):,}".replace(",", ".") if pd.notnull(x) else ""
        )

    # -------- VALOR DE AVALIAÇÃO --------
    if "Valor de avaliação" in df.columns:
        df["Valor Avaliação Num"] = pd.to_numeric(
            df["Valor de avaliação"],
            errors="coerce"
        )

        df["Valor de avaliação"] = df["Valor Avaliação Num"].apply(
            lambda x: f"{int(x):,}".replace(",", ".") if pd.notnull(x) else ""
        )

    # -------- DESCONTO --------
    if "Desconto ok" in df.columns:

        df["Desconto Num"] = pd.to_numeric(
            df["Desconto ok"],
            errors="coerce"
        )

        df["Desconto ok"] = df["Desconto Num"].apply(
            lambda x: f"{round(x*100)}%" if pd.notnull(x) else ""
        )

    df = df.fillna("")

    print("\n===== TESTE ENDEREÇOS =====")
    print("Endereço.......:", df.iloc[0].get("Endereço"))
    print("Endereço Mapa..:", df.iloc[0].get("Endereço Mapa"))
    print("===========================\n")

    imoveis = df.to_dict(orient="records")

    return render_template("index.html", imoveis=imoveis)

if __name__ == "__main__":
    app.run(debug=True)
