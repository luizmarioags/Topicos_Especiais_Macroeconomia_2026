# Especificação matemática do M3E

## 1. Notação

| Símbolo | Nome no código | Interpretação |
|---|---|---|
| $y$ | `y` | produto efetivo |
| $y^{*}$ | `y_potential` | produto potencial |
| $y_{AD}$ ou $y_{EXO}$ | `y_autonomous` | componente autônomo da demanda |
| $h = y-y^{*}$ | `h` | hiato do produto |
| $r^{e}$ | `r_expected` | taxa de juro real esperada |
| $r_{CB}$ | `r_cb` | estimativa do juro natural pelo Banco Central |
| $r^{*}$ | `r_natural` | taxa de juro natural verdadeira |
| $\pi$ | `pi` | inflação efetiva |
| $\pi^{e}$ | `pi_expected` | expectativa de inflação de curto prazo |
| $\pi^{*}$ | `pi_long_run` | expectativa de inflação de longo prazo |
| $\pi_{GOV}$ | `pi_target` | meta de inflação |

As taxas são armazenadas como proporções: `0.035` significa 3,5%.

## 2. Modelo estático

As quatro hipóteses implementadas na planilha são:

```math
\begin{aligned}
y &= y_{AD} - \gamma r^{e}, \\
\pi^{e} &= \theta\pi + (1-\theta)\pi^{*}, \\
\pi &= \pi^{e} + \alpha(y-y^{*}), \\
r^{e} &= r_{CB} + \phi_{\pi}(\pi^{e}-\pi_{GOV}).
\end{aligned}
```

A taxa natural é uma variável derivada:

```math
r^{*} = \frac{y_{AD}-y^{*}}{\gamma}.
```

### 2.1 Forma matricial exatamente igual à planilha

O Excel ordena as incógnitas como:

```math
x =
\begin{bmatrix}
y &
\pi^{e} &
\pi &
r^{e}
\end{bmatrix}^{\top}.
```

Portanto:

```math
\underbrace{
\begin{bmatrix}
1 & 0 & 0 & \gamma \\
0 & 1 & -\theta & 0 \\
-\alpha & -1 & 1 & 0 \\
0 & -\phi_{\pi} & 0 & 1
\end{bmatrix}
}_{A}
\underbrace{
\begin{bmatrix}
y \\
\pi^{e} \\
\pi \\
r^{e}
\end{bmatrix}
}_{x}
=
\underbrace{
\begin{bmatrix}
y_{AD} \\
(1-\theta)\pi^{*} \\
-\alpha y^{*} \\
r_{CB}-\phi_{\pi}\pi_{GOV}
\end{bmatrix}
}_{b}.
```

Assim,

```math
x = A^{-1}b.
```

Os slides exibem, em alguns pontos, uma ordem alternativa das incógnitas. O
pacote preserva a ordem efetivamente usada pelas fórmulas do Excel.

### 2.2 Parâmetros e soluções de referência

| Parâmetro | Equilíbrio 1 | Equilíbrio 2 |
|---|---:|---:|
| $y^{*}$ | 1,000 | 1,000 |
| $y_{AD}$ | 1,100 | 1,200 |
| $r^{*}$, derivado | 5,00% | 10,00% |
| $r_{CB}$ | 5,00% | 5,00% |
| $\pi^{*}$ | 3,50% | 3,50% |
| $\pi_{GOV}$ | 3,50% | 3,50% |
| $\gamma$ | 2,000 | 2,000 |
| $\theta$ | 0,300 | 0,300 |
| $\alpha$ | 0,250 | 0,250 |
| $\phi_{\pi}$ | 1,500 | 1,500 |

| Variável | Equilíbrio 1 | Equilíbrio 2 | Desvio absoluto |
|---|---:|---:|---:|
| $y$ | 1,0000000000 | 1,0756756757 | 0,0756756757 |
| $\pi^{e}$ | 0,0350000000 | 0,0431081081 | 0,0081081081 |
| $\pi$ | 0,0350000000 | 0,0620270270 | 0,0270270270 |
| $r^{e}$ | 0,0500000000 | 0,0621621622 | 0,0121621622 |

## 3. Modelo dinâmico

A implementação completa da planilha contém expectativas de longo prazo
parcialmente desancoradas e histerese:

```math
\begin{aligned}
y_{AD,t}
&= y_{AD,t-1} + \varepsilon_{AD,t},
\\[4pt]
y_t^{*}
&= (1-\eta)y_{t-1}^{*}
+ \eta y_{t-1}
+ \varepsilon_{y^{*},t},
\\[4pt]
r_{CB,t}
&= r_{CB,t-1}
+ \phi_y(y_{t-1}-y_{t-1}^{*})
+ \varepsilon_{r,t},
\\[4pt]
\pi_t^{*}
&= (1-\chi)\pi_{GOV}
+ \chi\pi_{t-1}
+ \varepsilon_{\pi^{*},t},
\\[4pt]
\pi_t^{e}
&= \theta\pi_{t-1}
+ (1-\theta)\pi_t^{*}
+ \varepsilon_{\pi^{e},t},
\\[4pt]
r_t^{e}
&= r_{CB,t}
+ \phi_{\pi}(\pi_t^{e}-\pi_{GOV}),
\\[4pt]
y_t
&= y_{AD,t}
- \gamma r_t^{e}
+ \varepsilon_{IS,t},
\\[4pt]
\pi_t
&= \pi_t^{e}
+ \alpha(y_t-y_t^{*})
+ \varepsilon_{\pi,t}.
\end{aligned}
```

As variáveis auxiliares são:

```math
h_t = y_t-y_t^{*},
```

e

```math
r_t^{*}
=
\frac{y_{AD,t}-y_t^{*}}{\gamma}.
```

O arquivo Excel aplica apenas

```math
\varepsilon_{AD,0}=0{,}01,
```

enquanto todos os demais choques são zero. Como o choque é uma inovação no
nível de $y_{AD}$, seu efeito é permanente.

### 3.1 Parâmetros da planilha dinâmica

```math
\gamma = 2,
\qquad
\theta = 0{,}3,
\qquad
\alpha = 0{,}25,
\qquad
\phi_{\pi} = 1{,}5,
```

```math
\phi_y = 0{,}25,
\qquad
\chi = 0{,}10,
\qquad
\eta = 0{,}05,
\qquad
\pi_{GOV} = 0{,}035.
```

A condição inicial em $t=-1$ é:

```math
y = y^{*} = 1,
\qquad
y_{AD} = 1{,}1,
```

```math
r^{e} = r_{CB} = r^{*} = 0{,}05,
```

e

```math
\pi = \pi^{e} = \pi^{*} = \pi_{GOV} = 0{,}035.
```

### 3.2 Forma reduzida matricial

Defina o estado mínimo:

```math
s_t =
\begin{bmatrix}
y_t &
y_t^{*} &
y_{AD,t} &
r_{CB,t} &
\pi_t
\end{bmatrix}^{\top}.
```

O pacote produz programaticamente:

```math
z_t = c + A s_{t-1} + B\varepsilon_t,
```

onde `z_t` contém, nesta ordem:

```text
h, y, y_potential, y_autonomous, r_expected, r_cb,
r_natural, pi, pi_expected, pi_long_run, pi_target
```

e o vetor de choques é:

```text
demand, is, inflation, potential, policy,
expectations_short, expectations_long
```

As linhas de $A$, $B$ e $c$ correspondentes ao estado formam:

```math
s_t = g + Fs_{t-1} + G\varepsilon_t.
```

Tanto a simulação recursiva quanto a simulação matricial são expostas e
testadas entre si.

## 4. Gráficos reproduzidos

- hiato do produto;
- produto efetivo e potencial;
- taxa de juro real esperada e estimativa do juro natural pelo BC;
- inflação efetiva e expectativas de curto e longo prazo;
- painel dinâmico com os quatro gráficos;
- comparação estática das curvas IS, Phillips e regra monetária.

Por padrão, os gráficos dinâmicos mostram $t=-1$ a $t=25$, intervalo
visível nos gráficos da planilha, embora a simulação e os CSVs contenham todas
as 511 observações.
