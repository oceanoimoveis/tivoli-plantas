# Monte Tivoli · Publicacao

Esta pasta contem a versao pronta para publicar no GitHub Pages.

## Estrutura

- `index.html`: pagina principal mobile-first
- `data/units.json`: 200 apartamentos com valores exatos da tabela oficial
- `assets/`: plantas, torre, ficha tecnica, logo e galeria otimizados
- `scripts/build_units.py`: recria `data/units.json` a partir do PDF oficial

## Publicar no GitHub Pages

1. Crie ou abra um repositorio no GitHub.
2. Envie o conteudo desta pasta para a raiz do repositorio, ou para a pasta `docs/`.
3. No GitHub, abra `Settings > Pages`.
4. Em `Build and deployment`, escolha:
   - `Deploy from a branch`
   - branch `main`
   - pasta `/root` ou `/docs`, conforme onde voce enviou os arquivos
5. Aguarde o link ser gerado pelo GitHub Pages.

## Teste local

Para testar no computador antes de publicar, rode um servidor simples na pasta:

```powershell
cd C:\Users\Vini\Documents\Claude\TIVOLI\lovable_publish
python -m http.server 8000
```

Depois abra `http://localhost:8000`.

Se voce abrir o `index.html` com duplo clique, alguns navegadores bloqueiam a leitura do `data/units.json`.

## Atualizar a tabela

Se chegar uma nova tabela oficial:

1. Substitua o PDF usado em `scripts/build_units.py`
2. Rode:

```powershell
python lovable_publish/scripts/build_units.py
```

3. Suba novamente `data/units.json`

## Observacao

Os valores exibidos nos cards saem da tabela PDF oficial, unidade por unidade.
