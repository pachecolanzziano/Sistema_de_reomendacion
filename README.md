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
12. [Evaluación](#-evaluación)
13. [Limitaciones Técnicas](#-limitaciones-técnicas)
14. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
15. [Estructura del Proyecto](#-estructura-del-proyecto)
16. [Impacto y Viabilidad de Negocio](#-impacto-y-viabilidad-de-negocio)
17. [Instalación](#-instalación)
18. [Configuración del Entorno](#-configuración-del-entorno)
19. [Ejecución del Proyecto](#-ejecución-del-proyecto)
20. [Estado del Proyecto — Demo 1](#-estado-del-proyecto--demo-1)
21. [Equipo](#-equipo)

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
- Evaluar la capacidad de los modelos para recomendar productos relevantes.
- Comparar el desempeño del modelo personalizado frente al baseline.
- Establecer una base técnica para futuras etapas de integración y despliegue.

---

## 📊 KPIs

Los indicadores principales definidos para medir el impacto comercial de la solución son:

| KPI | Objetivo |
|---|---|
| **KPI principal: Incremento del ticket promedio por cliente** | Medir el aumento del valor promedio de compra asociado a las recomendaciones. |
| **KPI secundario: Incremento en las ventas de productos recomendados** | Medir el crecimiento de las ventas correspondientes a productos sugeridos por el sistema. |

> Estos KPIs corresponden a indicadores de negocio. La evaluación técnica del sistema se realiza mediante métricas de recomendación como **Precision@10**.

---

## 📦 Dataset y Fuentes de Datos

### Fuente

El proyecto utiliza el dataset público **Online Retail II — UCI**, disponible en Kaggle:

https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci

El dataset contiene transacciones realizadas por una empresa de venta minorista en línea registrada en Reino Unido, entre el **1 de diciembre de 2009 y el 9 de diciembre de 2011**.

La empresa comercializa principalmente artículos de regalo y una parte importante de sus clientes corresponde a compradores mayoristas.

### Dataset utilizado

El dataset original contiene aproximadamente **1.067.371 registros**.

Después de las etapas de limpieza y preparación, la versión de trabajo considerada actualmente contiene:

> **779.425 registros — valor pendiente de validación final con el equipo.**

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

> **Nota de alcance Demo 1:** El análisis de **FP-Growth** no forma parte de la solución implementada y, por lo tanto, no se considera dentro del alcance actual del proyecto.

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

A partir de los hallazgos del EDA y de la matriz de interacción Cliente × Producto, se implementaron dos enfoques complementarios:

1. **Popularity Baseline**
2. **Item-Based Collaborative Filtering**

El baseline permite establecer un punto de comparación objetivo, mientras que el modelo Item-Based busca incorporar personalización a partir de las relaciones entre productos.

## 📌 Alcance del Sistema

| Elemento | Definición |
|---|---|
| **Tipo de recomendación** | Productos relacionados / complementarios |
| **Entrada** | Historial transaccional Cliente × Producto |
| **Interacción** | Cantidad acumulada comprada |
| **Salida** | Top 10 productos recomendados |
| **Personalización** | Baseline: no / Item-Based: sí |
| **Objetivo comercial** | Apoyar Cross Selling |

### Flujo general

```text
Historial transaccional
          ↓
Limpieza y preparación
          ↓
Matriz Cliente × Producto
          ↓
   ┌──────┴──────┐
   ↓             ↓
Popularity     Item-Based
Baseline          CF
   ↓             ↓
   └──────┬──────┘
          ↓
       Top 10
          ↓
     Evaluación
          ↓
   Impacto de negocio
```

---

# 📈 Popularity Baseline

El **Popularity Baseline** funciona como modelo de referencia.

Su estrategia consiste en recomendar a todos los clientes los mismos productos con mayor cantidad acumulada de unidades vendidas dentro del conjunto de entrenamiento.

### Funcionamiento

1. Se utiliza únicamente el conjunto `Train`.
2. Se calcula la cantidad total vendida por producto.
3. Los productos se ordenan de mayor a menor cantidad.
4. Se seleccionan los **Top 10 productos**.
5. Los mismos productos se utilizan como recomendaciones para los clientes evaluados.

Este enfoque **no es personalizado**.

Su propósito es establecer un punto de comparación:

> Si el modelo personalizado no supera al baseline de popularidad, no estaría demostrando un valor adicional suficiente frente a una estrategia comercial mucho más sencilla.

La implementación se encuentra en:

```text
src/ItemBased_CF/popularity_baseline.py
```

---

# 🧠 Item-Based Collaborative Filtering

El segundo enfoque implementado corresponde a un sistema de **Collaborative Filtering basado en ítems**.

En lugar de recomendar únicamente los productos más populares, el modelo utiliza las relaciones existentes entre los productos que los clientes han comprado.

## Principio de funcionamiento

El modelo parte de la matriz:

**Cliente × Producto**

y calcula la similitud entre productos utilizando **similitud coseno**.

```text
Matriz Cliente × Producto
          ↓
Similitud entre productos
          ↓
Productos relacionados
          ↓
Historial del cliente
          ↓
Puntuación de candidatos
          ↓
       Top 10
```

La similitud entre ítems se obtiene utilizando `cosine_similarity` de `scikit-learn`.

## Generación de recomendaciones

Para un cliente determinado:

1. Se identifica su historial de productos comprados.
2. Se toman las similitudes de esos productos con el resto del catálogo.
3. Se agregan las señales de similitud para obtener una puntuación por producto.
4. Se ordenan los candidatos según su puntuación.
5. Se seleccionan los **10 productos con mayor puntuación**.
6. Se pueden excluir productos que el cliente ya compró.

La implementación se encuentra en:

```text
src/ItemBased_CF/item_based_cf.py
```

---

## 🚫 Exclusión de Productos Ya Comprados

El sistema contempla dos escenarios:

| Escenario | Configuración | Descripción |
|---|---|---|
| **Nuevos productos** | `exclude_seen=True` | Excluye productos que el cliente ya compró. |
| **Recompras permitidas** | `exclude_seen=False` | Permite productos previamente adquiridos. |

Para el objetivo principal de **Cross Selling**, el escenario de exclusión de productos previamente adquiridos resulta especialmente relevante porque busca identificar oportunidades adicionales de compra.

---

# 📏 Evaluación

La evaluación busca determinar si las recomendaciones generadas permiten recuperar productos que el cliente realmente compró posteriormente.

Se utiliza la separación temporal **80/20**, donde el 20 % más reciente corresponde al conjunto de prueba.

## Precision@10

La métrica principal definida para la evaluación es:

**Precision@10**

Esta métrica mide qué proporción de los 10 productos recomendados corresponde a productos que aparecen posteriormente en el conjunto de prueba del cliente.

Conceptualmente:

```text
Precision@10 =
productos recomendados que aparecen en test
-------------------------------------------
                  10
```

### Protocolo de evaluación

```text
                DATASET
                   │
                   ▼
          Ordenamiento temporal
                   │
                   ▼
             ┌─────────┐
             │  TRAIN  │ 80 %
             └────┬────┘
                  │
        Matriz Cliente × Producto
                  │
          ┌───────┴────────┐
          ▼                ▼
     Popularity        Item-Based
      Baseline             CF
          │                │
          └───────┬────────┘
                  ▼
                Top 10
                  │
                  ▼
          Comparación con Test
                  │
                  ▼
             Precision@10
```

## Comparación de Modelos

La tabla queda preparada para incorporar los resultados definitivos de la ejecución:

| Modelo | Personalización | Top-K | Precision@10 | Estado |
|---|---|---:|---:|---|
| **Popularity Baseline** | ❌ No | 10 | **Pendiente** | Implementado |
| **Item-Based CF** | ✅ Sí | 10 | **Pendiente** | Implementado |

> **Nota:** Los valores de Precision@10 se incorporarán después de ejecutar ambos modelos sobre la versión definitiva y validada del dataset.

---

# 🧪 Interpretación de Resultados

La comparación permitirá responder una pregunta central:

> **¿El modelo personalizado logra recomendar productos relevantes mejor que una estrategia basada únicamente en popularidad?**

### Si Item-Based CF supera al baseline

Esto indicaría que las relaciones entre productos aportan información adicional frente a recomendar únicamente los productos más vendidos.

### Si el baseline supera al Item-Based CF

Esto indicaría que la personalización implementada todavía no genera suficiente valor predictivo y sería necesario revisar aspectos como:

- Sparsity.
- Long Tail.
- Cantidad de interacciones por cliente.
- Cantidad de interacciones por producto.
- Estrategia de scoring.
- Tratamiento de clientes con poco historial.

---

# 🧩 Justificación del Enfoque

## ¿Por qué utilizar un baseline?

El baseline de popularidad proporciona una referencia sencilla, interpretable y reproducible.

Permite determinar si el sistema desarrollado aporta valor adicional frente a una estrategia que solamente utiliza la frecuencia de compra.

Además, evita evaluar el modelo personalizado de manera aislada.

## ¿Por qué Item-Based Collaborative Filtering?

El enfoque Item-Based resulta adecuado para este escenario porque el problema se basa en las relaciones existentes entre productos comprados por los clientes.

El modelo utiliza directamente los patrones de interacción presentes en el historial transaccional para identificar productos relacionados.

Esto permite:

- Identificar productos relacionados.
- Generar recomendaciones a partir del historial individual.
- Personalizar el Top 10 para cada cliente.
- Apoyar estrategias de Cross Selling.

---

# ⚖️ Comparación de Enfoques

| Aspecto | Popularity Baseline | Item-Based CF |
|---|---|---|
| Personalización | ❌ | ✅ |
| Complejidad | Baja | Media |
| Interpretabilidad | Alta | Media |
| Utiliza historial individual | ❌ | ✅ |
| Captura relaciones entre productos | ❌ | ✅ |
| Sensibilidad a popularidad | Alta | Media/Alta |
| Sensibilidad a sparsity | Baja | Mayor |


---

# 🛠️ Tecnologías Utilizadas

| Categoría | Herramientas |
|---|---|
| **Lenguaje** | Python |
| **Manipulación de datos** | Pandas, NumPy |
| **Matriz dispersa** | SciPy |
| **Machine Learning** | Scikit-Learn |
| **Similitud** | Cosine Similarity |
| **EDA y visualización** | Jupyter Notebook, Matplotlib, Seaborn, Plotly |
| **Control de versiones** | Git, GitHub |
| **Despliegue previsto** | FastAPI / Streamlit |

Las dependencias técnicas se encuentran documentadas en `requirements.txt`.

> **Nota:** Algunas herramientas forman parte de la infraestructura prevista para etapas posteriores. En Demo 1 el foco está en EDA, preparación de datos y primera implementación de los modelos de recomendación.

---

# 🗂️ Estructura del Proyecto

```text
Sistema_de_recomendacion/
│
├── src/
│   │
│   └── ItemBased_CF/
│       │
│       ├── __pycache__/
│       ├── DataSetLimpio.csv
│       ├── ft_engineering.py
│       ├── item_based_cf.py
│       ├── popularity_baseline.py
│       └── requirements.txt
│
├── EDA_data_set.ipynb
│
├── main.py
│
└── README.md
```

## Función de los principales archivos

| Archivo | Función |
|---|---|
| `EDA_data_set.ipynb` | Análisis exploratorio y diagnóstico de calidad de datos. |
| `DataSetLimpio.csv` | Dataset preparado para las etapas de modelado. |
| `ft_engineering.py` | Preprocesamiento, split temporal y construcción de la matriz Cliente × Producto. |
| `item_based_cf.py` | Implementación del Item-Based Collaborative Filtering y evaluación. |
| `popularity_baseline.py` | Implementación del baseline basado en popularidad. |
| `requirements.txt` | Dependencias del proyecto. |
| `main.py` | Punto de entrada reservado para la integración final. |
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
              ┌─────────┴─────────┐
              ▼                   ▼
       Popularity Baseline    Item-Based CF
              │                   │
              └─────────┬─────────┘
                        ▼
                     Top 10
                        │
                        ▼
                  Precision@10
                        │
                        ▼
               Comparación técnica
                        │
                        ▼
                Impacto de negocio
```

---

# 💰 Impacto y Viabilidad de Negocio

La solución busca generar valor mediante recomendaciones que puedan apoyar estrategias de **Cross Selling**, con impacto esperado principalmente sobre:

- **Ticket promedio por cliente.**
- **Ventas de productos recomendados.**

La viabilidad económica se documentará mediante un escenario basado en:

1. Inversión estimada del desarrollo.
2. Ticket promedio del dataset.
3. Porcentaje esperado de incremento asociado a las recomendaciones.
4. Porcentaje de clientes/facturas impactadas.
5. Beneficio económico estimado.
6. ROI potencial.

## Escenario económico — pendiente de validación

| Variable | Valor | Estado |
|---|---:|---|
| Ticket promedio | **USD 476,43** | Disponible |
| Incremento esperado | **5 %** | Hipótesis de escenario |
| Facturas/clientes impactados | **Pendiente** | Por validar |
| Beneficio estimado | **Pendiente** | Por calcular |
| Inversión estimada | **USD 6.000** | Escenario de trabajo |
| ROI | **Pendiente** | Por calcular |

### Fórmula conceptual

```text
Beneficio estimado
=
Ticket promedio
×
Incremento esperado
×
Facturas impactadas
```

```text
ROI
=
(Beneficio estimado - Inversión)
--------------------------------
          Inversión
```

> **Nota:** El escenario económico se considera preliminar y deberá validarse con los datos definitivos de los modelos y con los supuestos comerciales acordados por el equipo.

> **Escenario conservador:** el ROI debe interpretarse como una estimación inicial y no como un resultado financiero garantizado. La adopción real de las recomendaciones y su conversión comercial deberán validarse mediante un piloto controlado.

---

# ⚙️ Instalación

Esta sección permite preparar el proyecto desde cero en un equipo nuevo y reproducir el entorno utilizado para el desarrollo.

## 1. Clonar el repositorio

```bash
git clone https://github.com/pachecolanzziano/Sistema_de_recomendacion.git
```

## 2. Ingresar al proyecto

```bash
cd Sistema_de_recomendacion
```

## 3. Verificar Python

Se recomienda utilizar **Python 3.11 o superior**.

```bash
python --version
```

Si el comando anterior no funciona en Windows, puede utilizarse:

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

### Windows — CMD

```bash
venv\Scripts\activate
```

### Windows — PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
source venv/bin/activate
```

Una vez activado, el entorno virtual aparecerá normalmente al inicio de la terminal como `(venv)`.

## 2. Actualizar pip

```bash
python -m pip install --upgrade pip
```

## 3. Instalar dependencias

Las dependencias utilizadas por el proyecto se encuentran actualmente en:

```text
src/ItemBased_CF/requirements.txt
```

Desde la raíz del proyecto:

```bash
pip install -r src/ItemBased_CF/requirements.txt
```

Entre las principales dependencias se encuentran **Pandas, NumPy, SciPy, Scikit-Learn, Matplotlib, Seaborn, Plotly y Jupyter**. Las dependencias también contemplan herramientas previstas para etapas posteriores, como FastAPI, Uvicorn, Joblib y Streamlit.

## 4. Verificar la instalación

```bash
python -c "import pandas, numpy, scipy, sklearn; print('Entorno configurado correctamente')"
```

> **Nota:** El proyecto utiliza un archivo de dependencias para facilitar la reproducibilidad del entorno entre los integrantes del equipo.

---

# ▶️ Ejecución del Proyecto

En Demo 1, el proyecto puede ejecutarse en dos partes principales: **EDA** y **modelos de recomendación**.

## 1. Ejecutar el EDA

El análisis exploratorio se encuentra en:

```text
EDA_data_set.ipynb
```

Desde la raíz del repositorio se puede iniciar Jupyter Notebook con:

```bash
jupyter notebook
```

Posteriormente, abrir:

```text
EDA_data_set.ipynb
```

El notebook documenta la exploración, diagnóstico de calidad y análisis inicial del dataset.

## 2. Ejecutar los modelos de recomendación

Los scripts de recomendación se encuentran en:

```text
src/ItemBased_CF/
```

Es importante ejecutar los modelos desde esa carpeta porque los scripts utilizan el archivo `DataSetLimpio.csv` mediante una ruta relativa y comparten el módulo `ft_engineering.py`.

```bash
cd src/ItemBased_CF
```

### Popularity Baseline

```bash
python popularity_baseline.py
```

El script calcula el **Precision@10 promedio**, el número de clientes evaluados y muestra los 10 productos más populares utilizados como recomendación.

### Item-Based Collaborative Filtering

```bash
python item_based_cf.py
```

El script calcula:

- Precision@10 excluyendo productos ya comprados.
- Precision@10 permitiendo recompras.
- Número de clientes evaluados.
- Un ejemplo de recomendaciones generadas para un cliente.

La implementación utiliza la matriz de interacción Cliente × Producto y similitud coseno entre productos.

## 3. Flujo de ejecución

```text
EDA_data_set.ipynb
        ↓
DataSetLimpio.csv
        ↓
ft_engineering.py
        ↓
Matriz Cliente × Producto
        ↓
   ┌────┴────┐
   ↓         ↓
Popularity  Item-Based CF
Baseline
   ↓         ↓
   └────┬────┘
        ↓
   Precision@10
```

## 4. Archivos necesarios para ejecutar los modelos

La ejecución de los modelos requiere que el dataset limpio esté disponible en:

```text
src/ItemBased_CF/DataSetLimpio.csv
```

y que los siguientes archivos se encuentren en la misma carpeta:

```text
src/ItemBased_CF/
├── DataSetLimpio.csv
├── ft_engineering.py
├── item_based_cf.py
├── popularity_baseline.py
└── requirements.txt
```

## 5. Punto de entrada `main.py`

Durante Demo 1, `main.py` permanece reservado para la integración final de la solución.

```text
main.py
```

Actualmente no contiene la lógica principal de ejecución. La integración hacia este punto de entrada se realizará en una etapa posterior, una vez consolidados los modelos y el flujo final del sistema.

> **Nota de reproducibilidad:** Para obtener resultados consistentes, debe utilizarse la misma versión validada de `DataSetLimpio.csv` y ejecutar el mismo protocolo temporal 80/20 definido en `ft_engineering.py`.

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
- División temporal Train/Test.
- Implementación del Popularity Baseline.
- Implementación del Item-Based Collaborative Filtering.
- Definición de Precision@10.
- Preparación de la comparación entre modelos.
- Documentación técnica inicial.

### 🔄 Pendiente para las siguientes etapas

- Validación definitiva del número de registros del dataset limpio.
- Ejecución y validación final de las métricas.
- Comparación definitiva de resultados.
- Ajustes y optimización de los modelos.
- Integración de la solución.
- Demo funcional.
- Despliegue / API / interfaz según el alcance final.
- Validación del impacto comercial.
- Consolidación del escenario económico y ROI.

> **Alcance Demo 1:** Esta entrega documenta y demuestra la comprensión del negocio, el análisis y preparación de datos y la primera implementación de la estrategia de recomendación. Las conclusiones definitivas, el roadmap y la solución final serán incorporados en la entrega final.

---

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