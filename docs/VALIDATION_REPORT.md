# Relatório de validação

## Escopo

A validação compara diretamente as saídas do código com os valores em cache
dos dois arquivos Excel fornecidos. As fórmulas não foram aproximadas por
regressão ou calibração: foram transcritas como sistema linear e recursões.

## Modelo estático

- matriz de coeficientes: igualdade elemento a elemento;
- vetor exógeno: igualdade elemento a elemento;
- matriz inversa: igualdade dentro da precisão de ponto flutuante;
- solução dos dois equilíbrios: tolerância absoluta de `1e-14`;
- maior resíduo observado em \(Ax-b\): `2.220446049250313e-16`.

## Modelo dinâmico

- horizonte: 511 observações (`t=-1` a `t=509`);
- colunas: mesma ordem das colunas `A:S` da planilha;
- cenário: inovação permanente de `0.01` na demanda autônoma em `t=0`;
- comparação das 511 linhas e 18 séries/parametros: tolerância absoluta de
  `2e-13`;
- simulação recursiva versus forma reduzida matricial: tolerância absoluta de
  `5e-14` no teste Python.

Valores de longo prazo reproduzidos:

| Variável | Excel em `t=509` | Python em `t=509` |
|---|---:|---:|
| `h` | 0 | 0 |
| `y` | 1.0009090909090885 | 1.0009090909090880 |
| `y_potential` | 1.0009090909090872 | 1.0009090909090880 |
| `y_autonomous` | 1.11 | 1.11 |
| `r_expected` | 0.05454545454545574 | 0.05454545454545597 |
| `r_cb` | 0.05454545454545574 | 0.05454545454545597 |
| `pi` | 0.035 | 0.035 |

As diferenças são inferiores a `8e-16` e decorrem apenas da ordem de operações
em ponto flutuante.

## Testes executados

O conjunto Python contém quatro testes automatizados:

1. soluções dos dois equilíbrios estáticos;
2. igualdade entre simulação recursiva e matricial;
3. igualdade da simulação com o CSV extraído do Excel;
4. dimensões e organização das matrizes dinâmicas.

Resultado observado: **4 testes aprovados**.

O pacote R inclui os mesmos testes em `tests/replication.R` e o mesmo CSV em
`inst/extdata/`. O ambiente usado para construir este artefato não continha um
interpretador R; por isso a execução local automatizada foi realizada no
Python, enquanto a implementação R foi mantida algébrica e estruturalmente
paralela.

