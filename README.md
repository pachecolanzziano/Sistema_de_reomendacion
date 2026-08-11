# 🧠 Sistema Inteligente de Recomendación de Productos — DataLab Consulting

### Sistema inteligente de recomendación desarrollado para un escenario de E-Commerce / Retail

**DataLab Consulting** propone una solución de recomendación de productos basada en el historial transaccional de clientes, orientada a identificar relaciones entre productos y generar recomendaciones relevantes que puedan apoyar estrategias comerciales de **Cross Selling**.

> **Estado:** Demo 1 — análisis, preparación de datos y primera implementación de modelos de recomendación.

---

## 📑 Tabla de Contenidos

1. [Introducción](#-introducción)
2. [Problema de Negocio](#-problema-de-negocio)
3. [Objetivos](#-objetivos)
4. [KPIs](#-kpis)
5. [Dataset y Fuentes de Datos](#-dataset-y-fuentes-de-datos)
6. [Análisis Exploratorio de Datos — EDA](#-análisis-exploratorio-de-datos--eda)
7. [Limpieza y Preparación de Datos](#-limpieza-y-preparación-de-datos)
8. [Feature Engineering](#-feature-engineering)
9. [Estrategia de Recomendación](#-estrategia-de-recomendación)
10. [Popularity Baseline](#-popularity-baseline)
11. [Item-Based Collaborative Filtering](#-item-based-collaborative-filtering)
12. [ALS — Alternating Least Squares](#-als--alternating-least-squares)
13. [FP-Growth](#-fp-growth)
14. [Evaluación de Modelos](#-evaluación-de-modelos)
15. [Interpretación de Resultados](#-interpretación-de-resultados)
16. [Limitaciones Técnicas](#-limitaciones-técnicas)
17. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
18. [Estructura del Proyecto](#-estructura-del-proyecto)
19. [Impacto y Viabilidad de Negocio](#-impacto-y-viabilidad-de-negocio)
20. [Instalación](#-instalación)
21. [Configuración del Entorno](#-configuración-del-entorno)
22. [Ejecución del Proyecto](#-ejecución-del-proyecto)
23. [Estado del Proyecto — Demo 1](#-estado-del-proyecto--demo-1)
24. [Equipo](#-equipo)

---

## 📖 Introducción

En un entorno de E-Commerce, el historial de transacciones representa una fuente importante de información para comprender el comportamiento de compra de los clientes.

El presente proyecto propone el desarrollo de un **sistema inteligente de recomendación de productos** capaz de utilizar las interacciones históricas entre clientes y productos para generar recomendaciones relevantes y personalizadas.

La solución busca apoyar principalmente estrategias comerciales de **Cross Selling**, conectando el comportamiento histórico de compra con oportunidades de recomendación de productos.

---

## 💼 Problema de Negocio

La empresa dispone de un historial transaccional considerable, pero actualmente no cuenta con un mecanismo de recomendación personalizado que permita aprovechar de manera sistemática las relaciones existentes entre los productos adquiridos por sus clientes.

Una estrategia basada únicamente en productos populares no considera las diferencias en los patrones de compra de cada cliente.

### Necesidad identificada

Desarrollar un sistema capaz de transformar el historial de compras en **recomendaciones de productos relevantes para cada cliente**, con potencial para apoyar el incremento del valor de las compras y la venta de productos recomendados.

---

## 🎯 Objetivos

### Objetivo Principal

**Desarrollar un sistema inteligente de recomendación de productos que aproveche el historial de compras para identificar relaciones entre productos y generar recomendaciones personalizadas que apoyen estrategias de Cross Selling.**

### Objetivos Específicos

- Analizar y comprender el comportamiento transaccional de los clientes mediante EDA.
- Identificar y tratar problemas de calidad presentes en los datos.
- Preparar una matriz de interacción Cliente × Producto.
- Implementar un **Popularity Baseline** como referencia de comparación.
- Implementar un modelo **Item-Based Collaborative Filtering**.
- Implementar un modelo de factorización **ALS — Alternating Least Squares**.
- Implementar **FP-Growth** 
- Evaluar la capacidad de los modelos para recomendar productos relevantes.
- Comparar el desempeño de los diferentes enfoques de recomendación.
- Establecer una base técnica para futuras etapas de integración y despliegue.

---

## 📊 KPIs

Los indicadores principales definidos para medir el impacto comercial de la solución son:

| KPI | Objetivo |
|---|---|
| **KPI principal: Incremento del 15% en el ticket promedio** | Medir el aumento del valor promedio de compra asociado a las recomendaciones. |
| **KPI secundario: Incremento en las ventas de productos recomendados** | Medir el crecimiento de las ventas correspondientes a productos sugeridos por el sistema. |

---

## 📦 Dataset y Fuentes de Datos

### Fuente

El proyecto utiliza el dataset público **Online Retail II — UCI**, disponible en Kaggle:

https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci

El dataset contiene transacciones realizadas por una empresa de venta minorista en línea registrada en Reino Unido, entre el **1 de diciembre de 2009 y el 9 de diciembre de 2011**.

La empresa comercializa principalmente artículos de regalo y una parte importante de sus clientes corresponde a compradores mayoristas.

### Dataset utilizado

El dataset original contiene aproximadamente **1.067.371 registros**.

Después de las etapas de limpieza y preparación, la versión de trabajo considerada actualmente contiene: **805.243 registros.**

### Variables relevantes

| Variable | Descripción |
|---|---|
| `InvoiceNo` | Identificador de la factura |
| `StockCode` | Identificador del producto |
| `Description` | Descripción del producto |
| `Quantity` | Cantidad de unidades compradas |
| `InvoiceDate` | Fecha y hora de la transacción |
| `UnitPrice` | Precio unitario |
| `CustomerID` | Identificador del cliente |
| `Country` | País asociado a la transacción |

### Calidad de los datos

Durante el análisis se identificaron problemas como:

- Valores nulos.
- Registros duplicados.
- Valores negativos en variables transaccionales.
- Cancelaciones o transacciones que deben ser tratadas antes del modelado.
- Alta concentración de transacciones en determinados productos.
- Diferencias importantes en la frecuencia de interacción entre clientes y productos.

### Justificación de la elección

El dataset permite abordar el problema porque contiene el historial transaccional necesario para estudiar:

- Productos adquiridos.
- Cantidades compradas.
- Clientes.
- Fechas de compra.
- Relaciones entre productos.
- Patrones de comportamiento de compra.

Estas características permiten construir una matriz de interacción y desarrollar modelos de recomendación basados en comportamiento histórico.

---

## 🔎 Análisis Exploratorio de Datos — EDA

El EDA permitió comprender la estructura del dataset y determinar qué información podía utilizarse para la construcción del sistema.

### Principales actividades realizadas

- Revisión de dimensiones del dataset.
- Identificación de tipos de variables.
- Análisis de valores nulos.
- Identificación de registros duplicados.
- Análisis de valores negativos.
- Revisión de distribuciones de `Quantity` y `UnitPrice`.
- Análisis temporal de las transacciones.
- Análisis de clientes y productos.
- Identificación de productos con mayor volumen de compra.
- Identificación de la concentración de interacciones.
- Análisis de la relación entre clientes y productos.

### Hallazgos relevantes

El análisis permitió identificar una distribución desigual de las interacciones:

- Algunos productos concentran una proporción importante de las compras.
- Existen productos con pocas interacciones.
- Los clientes presentan diferentes niveles de actividad.
- La matriz Cliente × Producto presenta una elevada dispersión.

Estos hallazgos justifican la comparación entre un modelo basado en popularidad y un modelo personalizado basado en similitud entre productos.

> **Nota de alcance Demo 1:** FP-Growth se incorpora como enfoque complementario para Cross Selling y se evalúa de forma independiente debido a que trabaja a nivel de factura.

---

## 🧹 Limpieza y Preparación de Datos

La preparación de datos busca generar una base consistente para las etapas posteriores de modelado.

### Procesos realizados

- Eliminación de registros que no cumplen las condiciones necesarias para el modelado.
- Tratamiento de valores nulos.
- Conversión de `InvoiceDate` a formato de fecha.
- Ordenamiento cronológico de las transacciones.
- Preparación de identificadores de cliente y producto.
- Consolidación de interacciones cliente-producto.
- Preparación del dataset para la división temporal Train/Test.

El resultado de esta etapa es el archivo:

```text
DataSetLimpio.csv
```

---

# ⚙️ Feature Engineering

El Feature Engineering se concentra en transformar el historial transaccional en una representación adecuada para los modelos de recomendación.

## Matriz de Interacción Cliente × Producto

La solución representa las interacciones mediante una matriz:

**Cliente × Producto**

Cada fila representa un cliente y cada columna representa un producto.

El valor de cada interacción corresponde a la **cantidad acumulada comprada** por el cliente para cada producto.

La implementación agrupa `Quantity` por `customer_code` e `item_code` y construye una matriz dispersa mediante `csr_matrix`.

```text
                    PRODUCTOS
                P1    P2    P3    P4    P5
              ┌─────┬─────┬─────┬─────┬─────┐
Cliente 1     │ 12  │  0  │  3  │  0  │  0  │
Cliente 2     │  0  │  5  │  0  │  8  │  0  │
Cliente 3     │  2  │  0  │  0  │  0  │  7  │
Cliente 4     │  0  │  0  │  4  │  1  │  0  │
              └─────┴─────┴─────┴─────┴─────┘
```

## División Train / Test

Se utiliza una división temporal **80/20**.

| Conjunto | Proporción | Característica |
|---|---:|---|
| `Train` | **80 %** | Transacciones más antiguas |
| `Test` | **20 %** | Transacciones más recientes |

El conjunto de prueba corresponde siempre a las compras más recientes del dataset.

Esto evita mezclar información futura con información histórica y permite evaluar el sistema de forma más cercana a un escenario real de recomendación.

## Exclusión de Variables

Para el modelado de interacción:

- `Country` no se utiliza como variable de interacción.
- `Description` no se utiliza para entrenar la similitud.
- `StockCode` representa el identificador del producto.
- `CustomerID` representa el identificador del cliente.
- `Quantity` representa la intensidad de la interacción.

`Description` se conserva únicamente para traducir los códigos de producto a nombres legibles al presentar las recomendaciones.

---

## ⚠️ Limitaciones a Considerar

### Sparsity

La matriz Cliente × Producto puede presentar una alta dispersión debido a que cada cliente interactúa solamente con una pequeña proporción del catálogo disponible.

Esto puede afectar la capacidad de encontrar relaciones entre productos con pocas interacciones.

### Long Tail

El historial puede presentar una concentración importante de interacciones en productos populares y una cola larga de productos con menor frecuencia de compra.

Esto puede favorecer productos populares y dificultar recomendaciones para productos con poca información histórica.

### Cold Start

Un cliente sin historial suficiente no puede beneficiarse completamente de una estrategia basada en sus interacciones anteriores.

De igual forma, un producto nuevo sin historial presenta dificultades para establecer similitudes con otros productos.

Estas limitaciones deberán considerarse durante la interpretación de resultados y en futuras etapas del sistema.

---

# 🤖 Estrategia de Recomendación

A partir de los hallazgos del EDA y de la matriz de interacción Cliente × Producto, se implementaron cuatro enfoques complementarios de recomendación:

1. **Popularity Baseline**
2. **Item-Based Collaborative Filtering**
3. **ALS — Alternating Least Squares**
4. **FP-Growth**

Los modelos permiten comparar estrategias basadas en popularidad, relaciones entre productos, preferencias latentes y asociaciones de compra.

## 📌 Alcance del Sistema

| Elemento | Definición |
|---|---|
| **Tipo de recomendación** | Productos relevantes, relacionados o complementarios |
| **Entrada** | Historial transaccional |
| **Interacción** | Cantidad acumulada comprada |
| **Salida** | Top 10 recomendaciones |
| **Objetivo comercial** | Apoyar estrategias de Cross Selling |

### Flujo general

```text
Historial transaccional
          ↓
Limpieza y preparación
          ↓
Matriz Cliente × Producto
          ↓
   ┌──────┼──────────┬──────────┐
   ↓      ↓          ↓          ↓
Popularidad  Item-Based    ALS      FP-Growth
   ↓          CF           ↓          ↓
   └──────────┴──────────┴──────────┘
                    ↓
              Recomendaciones
                    ↓
                  Top 10
                    ↓
                Evaluación
```

---

# 📈 Popularity Baseline

El **Popularity Baseline** funciona como modelo de referencia para comparar el desempeño de las estrategias personalizadas.

## ¿Qué hace?

Recomienda los productos con mayor cantidad acumulada de unidades vendidas durante el conjunto de entrenamiento.

## Funcionamiento

1. Utiliza únicamente el conjunto `Train`.
2. Calcula la cantidad total vendida por producto.
3. Ordena los productos de mayor a menor cantidad.
4. Selecciona los **Top 10 productos**.
5. Utiliza estos productos como recomendación para los clientes evaluados.

Este enfoque **no es personalizado** y permite establecer una referencia sencilla frente a los modelos personalizados.

### Implementación

```text
src/Modelos/popularity_baseline.py
```

---

# 🧠 Item-Based Collaborative Filtering

El **Item-Based Collaborative Filtering** recomienda productos relacionados con aquellos que el cliente ya ha comprado.

## ¿Qué hace?

Identifica relaciones entre productos a partir del comportamiento histórico de los clientes.

## Funcionamiento

1. Parte de la matriz Cliente × Producto.
2. Calcula la similitud entre productos mediante **similitud coseno**.
3. Utiliza el historial de cada cliente.
4. Genera candidatos relacionados con sus productos anteriores.
5. Ordena los candidatos por puntuación.
6. Selecciona el **Top 10**.

```text
Matriz Cliente × Producto
          ↓
Similitud entre productos
          ↓
Historial del cliente
          ↓
Ranking de candidatos
          ↓
       Top 10
```

El modelo incorpora personalización porque las recomendaciones dependen del historial de compra de cada cliente.

### Implementación

```text
src/Modelos/item_based_cf.py
```

---

# 🧮 ALS — Alternating Least Squares

**ALS (Alternating Least Squares)** es un modelo de factorización matricial que busca identificar patrones de preferencia entre clientes y productos.

## ¿Qué hace?

Aprende representaciones latentes de clientes y productos a partir de las interacciones históricas y utiliza esas representaciones para generar recomendaciones.

## Funcionamiento

```text
Matriz Cliente × Producto
          ↓
     Factores latentes
          ↓
Preferencias aprendidas
          ↓
Ranking de productos
          ↓
       Top 10
```

ALS trabaja con **feedback implícito**, utilizando las interacciones de compra registradas en el historial.

### Implementación

```text
src/Modelos/als_model.py
```

---

# 🛒 FP-Growth

**FP-Growth** utiliza reglas de asociación para identificar productos que suelen aparecer juntos dentro de una misma factura.

## ¿Qué hace?

Permite identificar oportunidades de **Cross Selling** basadas en productos comprados conjuntamente.

## Funcionamiento

1. Agrupa los productos por factura.
2. Identifica productos que aparecen juntos con frecuencia.
3. Construye asociaciones entre productos.
4. Genera recomendaciones relacionadas con un producto de referencia.

```text
Facturas
   ↓
Productos comprados juntos
   ↓
Patrones de co-ocurrencia
   ↓
Reglas de asociación
   ↓
Productos relacionados
```

A diferencia de los modelos cliente-producto, FP-Growth trabaja a nivel de **factura**.

Por esta razón, su evaluación se realiza de forma independiente.

### Implementación

```text
src/Modelos/Modelos_juntos.py
```

---

# 📏 Evaluación de Modelos

La evaluación busca determinar qué tan relevantes son las recomendaciones generadas por cada enfoque frente al comportamiento observado posteriormente en los datos de prueba.

Se utiliza una separación temporal **80/20**:

| Conjunto | Proporción | Característica |
|---|---:|---|
| `Train` | **80 %** | Transacciones más antiguas |
| `Test` | **20 %** | Transacciones más recientes |

Esto evita mezclar información futura con información histórica y permite evaluar el sistema de una forma más cercana a un escenario real.

## Métricas utilizadas

### Precision@10

Mide qué proporción de los 10 productos recomendados aparece posteriormente entre las compras observadas en `Test`.

**Pregunta que responde:**

> ¿Qué tan acertadas son las recomendaciones?

### Recall@10

Mide qué proporción de los productos que el cliente compró posteriormente logró recuperar el Top 10 recomendado.

**Pregunta que responde:**

> ¿Qué parte del comportamiento posterior del cliente logramos cubrir?

### MAP@10

Evalúa la calidad del ranking considerando también la posición de los aciertos dentro del Top 10.

**Pregunta que responde:**

> ¿Los productos relevantes aparecen en las primeras posiciones?

### Coverage@10

Mide qué porcentaje del catálogo aparece al menos una vez entre las recomendaciones generadas.

**Pregunta que responde:**

> ¿El modelo recomienda una variedad amplia del catálogo?

---

## Resultados — Modelos evaluados sobre clientes

Popularity Baseline, Item-Based CF y ALS se evaluaron sobre **2.285 clientes**.

| Modelo | Precision@10 | Recall@10 | MAP@10 | Coverage@10 |
|---|---:|---:|---:|---:|
| **Popularity Baseline** | 0.0773 | 0.0243 | 0.0378 | 0.0022 |
| **Item-Based CF** | 0.1162 | 0.0575 | 0.0827 | **0.3931** |
| **ALS** | **0.1648** | **0.0814** | **0.1000** | 0.2762 |

### Principales resultados

**ALS presenta el mejor desempeño general en:**

- Precision@10: **0.1648**
- Recall@10: **0.0814**
- MAP@10: **0.1000**

**Item-Based CF presenta la mayor cobertura:**

- Coverage@10: **39,31 %**
- ALS: **27,62 %**

Esto muestra que ALS obtiene mejores resultados en precisión y calidad del ranking, mientras que Item-Based CF ofrece una mayor diversidad de productos recomendados.

---

## Resultados — FP-Growth

FP-Growth se evalúa de manera independiente porque su unidad de análisis es la **factura**.

| Modelo | Precision@10 | Recall@10 | MAP@10 | Coverage@10 |
|---|---:|---:|---:|---:|
| **Popularity Baseline** | 0.0773 | 0.0243 | 0.0378 | 0.0022 |
| **FP-Growth** | **0.1404** | **0.1042** | **0.1098** | **0.4583** |

FP-Growth supera al baseline dentro de su comparación en las cuatro métricas.

Además, alcanza una cobertura de **45,83 % del catálogo**.

> **Importante:** los resultados de FP-Growth no deben compararse directamente con los resultados de ALS e Item-Based CF, debido a que FP-Growth utiliza una unidad de evaluación diferente: **5.710 facturas frente a 2.285 clientes**.

---

# 🎯 Interpretación de Resultados

Los resultados permiten identificar diferentes fortalezas entre los modelos:

| Modelo | Principal fortaleza | Enfoque |
|---|---|---|
| **Popularity Baseline** | Referencia | Popularidad global |
| **Item-Based CF** | Cobertura y explicabilidad | Relaciones entre productos |
| **ALS** | Precisión y ranking | Preferencias aprendidas |
| **FP-Growth** | Cross Selling y diversidad | Productos comprados conjuntamente |

### Resultado principal

> **ALS presenta el mejor desempeño general entre los modelos evaluados sobre clientes, destacándose en Precision@10, Recall@10 y MAP@10.**

### Resultado complementario

> **Item-Based CF mantiene una ventaja en cobertura del catálogo y ofrece recomendaciones basadas en relaciones directas entre productos.**

### Aplicación de FP-Growth

> **FP-Growth aporta un enfoque complementario para Cross Selling, identificando productos que suelen comprarse conjuntamente dentro de una misma factura.**

---

# ⚠️ Limitaciones Técnicas

### Sparsity

La matriz Cliente × Producto puede presentar una alta dispersión debido a que cada cliente interactúa solamente con una pequeña proporción del catálogo disponible.

Esto puede afectar la capacidad de encontrar relaciones entre productos con pocas interacciones.

### Long Tail

El historial puede presentar una concentración importante de interacciones en productos populares y una cola larga de productos con menor frecuencia de compra.

Esto puede favorecer productos populares y dificultar recomendaciones para productos con poca información histórica.

### Cold Start

Un cliente sin historial suficiente no puede beneficiarse completamente de una estrategia basada en sus interacciones anteriores.

De igual forma, un producto nuevo sin historial presenta dificultades para establecer similitudes con otros productos.

Estas limitaciones deberán considerarse durante la interpretación de resultados y en futuras etapas del sistema.

---

# 🛠️ Tecnologías Utilizadas

| Categoría | Herramientas |
|---|---|
| **Lenguaje** | Python |
| **Manipulación de datos** | Pandas, NumPy |
| **Matriz dispersa** | SciPy |
| **Machine Learning** | Scikit-Learn |
| **Recomendación / Factorización** | Implicit |
| **Reglas de asociación** | MLxtend |
| **Similitud** | Cosine Similarity |
| **EDA y visualización** | Jupyter Notebook, Matplotlib, Seaborn, Plotly |
| **Control de versiones** | Git, GitHub |
| **Despliegue previsto** | FastAPI / Streamlit |

Las dependencias del proyecto se encuentran documentadas en:

```text
requirements.txt
```

> **Nota:** FastAPI y Streamlit corresponden a componentes previstos para etapas posteriores de integración y despliegue. En Demo 1 el foco se encuentra en EDA, preparación de datos, construcción de la matriz de interacción e implementación y evaluación de los modelos de recomendación.

---

# 🗂️ Estructura del Proyecto

```text
Sistema_de_reomendacion/
│
├── src/
│   ├── Data/
│   │   └── DataSetLimpio.csv
│   │
│   └── Modelos/
│       ├── als_model.py
│       ├── ft_engineering.py
│       ├── item_based_cf.py
│       ├── Modelos_juntos.py
│       └── popularity_baseline.py
│
├── EDA_data_set.ipynb
├── requirements.txt
├── .gitignore
└── README.md
```

## Función de los principales archivos

| Archivo | Función |
|---|---|
| `EDA_data_set.ipynb` | Análisis exploratorio y diagnóstico de calidad de datos. |
| `src/Data/DataSetLimpio.csv` | Dataset limpio utilizado como base para las etapas de modelado. |
| `src/Modelos/ft_engineering.py` | Preparación de interacciones, división temporal y construcción de la matriz Cliente × Producto. |
| `src/Modelos/popularity_baseline.py` | Implementación del baseline basado en popularidad. |
| `src/Modelos/item_based_cf.py` | Implementación del modelo Item-Based Collaborative Filtering. |
| `src/Modelos/als_model.py` | Implementación del modelo ALS. |
| `src/Modelos/Modelos_juntos.py` | Integración y evaluación conjunta de los diferentes enfoques de recomendación. |
| `requirements.txt` | Dependencias necesarias para ejecutar el proyecto. |
| `README.md` | Documentación general del proyecto. |

---

# 🔁 Flujo Técnico Actual

```text
                 DATASET ORIGINAL
                        │
                        ▼
                   EDA / QA
                        │
                        ▼
             LIMPIEZA Y PREPARACIÓN
                        │
                        ▼
                DataSetLimpio.csv
                        │
                        ▼
               FEATURE ENGINEERING
                        │
                        ▼
             Split temporal 80 / 20
                        │
                        ▼
             Matriz Cliente × Producto
                        │
       ┌────────────────┼────────────────┐
       ▼                ▼                ▼
Popularity          Item-Based          ALS
Baseline                CF               │
       │                │                │
       └────────────────┼────────────────┘
                        ▼
                 Recomendaciones
                        │
                        ▼
                     Top 10
                        │
                        ▼
                    Evaluación
                        │
                        ▼
                Selección / análisis
                        │
                        ▼
               Impacto de negocio
```

FP-Growth complementa este flujo trabajando a nivel de factura:

```text
Facturas
   ↓
Productos comprados conjuntamente
   ↓
FP-Growth
   ↓
Reglas de asociación
   ↓
Recomendaciones para Cross Selling
```

# ⚙️ Instalación

Esta sección permite preparar el proyecto desde cero en un equipo nuevo y reproducir el entorno utilizado durante el desarrollo.

## 1. Clonar el repositorio

```bash
git clone https://github.com/pachecolanzziano/Sistema_de_reomendacion.git
```

## 2. Ingresar al proyecto

```bash
cd Sistema_de_reomendacion
```

## 3. Verificar Python

```bash
python --version
```

En Windows también puede utilizarse:

```bash
py --version
```

## 4. Crear el entorno virtual

### Windows

```bash
python -m venv venv
```

### Linux / macOS

```bash
python3 -m venv venv
```

---

# 🔌 Configuración del Entorno

## 1. Activar el entorno virtual

### Windows — PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### Windows — CMD

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 2. Actualizar pip

```bash
python -m pip install --upgrade pip
```

## 3. Instalar dependencias

Desde la raíz del proyecto:

```bash
pip install -r requirements.txt
```

## 4. Verificar la instalación

```bash
python -c "import pandas, numpy, scipy, sklearn; print('Entorno configurado correctamente')"
```

> Las dependencias adicionales para recomendación y asociación se encuentran especificadas en `requirements.txt`.

---

# ▶️ Ejecución del Proyecto

En Demo 1, el proyecto se divide principalmente en **EDA, preparación de datos y modelos de recomendación**.

## 1. Ejecutar el EDA

El análisis exploratorio se encuentra en:

```text
EDA_data_set.ipynb
```

Para iniciar Jupyter:

```bash
jupyter notebook
```

Posteriormente, abrir:

```text
EDA_data_set.ipynb
```

## 2. Ejecutar los modelos

Los modelos se encuentran en:

```text
src/Modelos/
```

### Popularity Baseline

```bash
python src/Modelos/popularity_baseline.py
```

### Item-Based Collaborative Filtering

```bash
python src/Modelos/item_based_cf.py
```

### ALS

```bash
python src/Modelos/als_model.py
```

### Modelos y evaluación conjunta

```bash
python src/Modelos/Modelos_juntos.py
```

> **Nota:** `Modelos_juntos.py` integra los diferentes enfoques de recomendación y permite realizar la evaluación comparativa definida para Demo 1.

## 3. Dataset utilizado

El dataset limpio se encuentra en:

```text
src/Data/DataSetLimpio.csv
```

La ejecución debe realizarse utilizando la estructura de carpetas actual del repositorio y la versión validada del dataset.

## 4. Punto de entrada `main.py`

Durante Demo 1, `main.py` permanece reservado para la integración final de la solución.

Actualmente no contiene la lógica principal de ejecución del sistema. La integración hacia este punto de entrada se realizará en una etapa posterior.

---

# 📌 Estado del Proyecto — Demo 1

### ✅ Completado

- Definición del problema de negocio.
- Definición del objetivo principal.
- Definición de KPIs.
- Análisis exploratorio del dataset.
- Identificación de problemas de calidad.
- Limpieza y preparación inicial de los datos.
- Construcción del dataset de trabajo.
- Feature Engineering.
- Construcción de la matriz Cliente × Producto.
- División temporal Train/Test 80/20.
- Implementación del Popularity Baseline.
- Implementación del Item-Based Collaborative Filtering.
- Implementación del modelo ALS.
- Implementación de FP-Growth como enfoque de asociación para Cross Selling.
- Integración de modelos mediante `Modelos_juntos.py`.
- Evaluación mediante Precision@10, Recall@10, MAP@10 y Coverage@10.
- Comparación de resultados.
- Identificación de fortalezas y limitaciones de cada enfoque.
- Preparación del escenario preliminar de impacto y viabilidad económica.
- Documentación técnica inicial del proyecto.

### 🔄 Pendiente para las siguientes etapas

- Validación definitiva del número de registros del dataset limpio.
- Validación final de resultados y supuestos con el equipo.
- Ajustes y optimización de los modelos.
- Integración completa de la solución.
- Desarrollo de la API.
- Desarrollo de la interfaz Streamlit.
- Demo funcional.
- Despliegue según el alcance final.
- Validación del impacto comercial mediante datos reales.
- Consolidación definitiva del escenario económico y ROI.
- Conclusiones finales y roadmap.

> **Alcance Demo 1:** Esta entrega documenta y demuestra la comprensión del negocio, el análisis y preparación de datos y la implementación y evaluación inicial de los modelos de recomendación. Las conclusiones definitivas, el roadmap y la solución final serán incorporados en las siguientes etapas.

# 👥 Equipo

### DataLab Consulting

**Misión**

> En DataLab Consulting transformamos datos en información estratégica, desarrollando soluciones de analítica e inteligencia artificial que permiten a las organizaciones tomar decisiones basadas en datos y generar valor para su negocio.

### Roles

| Integrante | Rol |
|---|---|
| **Daniel Ruiz** | Data Team |
| **Isaac Esquinca** | Data Team |
| **Luis Pacheco** | Data Team |
| **Jessica Roncancio** | Data Team |
| **Alejandro Zarzoza** | Data Team |
| **Ismael Hernández** | Data Team |
---