# m3e-replication (Python)

Implementação reproduzível do Modelo Macroeconômico de 3 Equações (M3E),
com a mesma parametrização, matrizes, simulação dinâmica e gráficos das
planilhas de referência.

```bash
python -m pip install .
m3e-replicate --output-dir outputs/python
```

Uso básico:

```python
from m3e import (
    excel_static_scenarios,
    excel_dynamic_shocks,
    simulate_dynamic,
    solve_static,
)

equilibrio_1, equilibrio_2 = excel_static_scenarios()
solucao_1 = solve_static(equilibrio_1)
solucao_2 = solve_static(equilibrio_2)

trajetoria = simulate_dynamic(
    shocks=excel_dynamic_shocks(horizon=509),
    horizon=509,
)
```

Consulte o `README.md` da raiz e `docs/MODEL_SPECIFICATION.md` para a
especificação matemática completa.

