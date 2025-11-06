# TT - Público

Código y archivos públicos de Trabajo Terminal II, no comerciables, solo informativos

* No se adjuntan archivos csv en este repositorio
* El código no funcionará si se corre, debido a que la forma del desarrollo de las noticias ha sido en diferentes entornos

* VMs Azure -> Extracción
* EDA --> Google Colab
* Base Cleaning --> Local
* Advanced Cleaning --> Google Colab
* Translation --> Kaggle TPUs x2

## Noticias

### Extracción

Para esto, el proceso de extracción se compone de cuatro etapas:

1. Se prepara un archivo con las configuraciones necesarias para la extracción de noticias.

2. Se procede con la creación de las URLs a consultar (también llamadas endpoints).

3. Posteriormente, se realiza un proceso de filtrado y limpieza de las URLs generadas.

4. Finalmente, se ejecuta la recolección de información desde la API de GDELT, registrando los resultados obtenidos.

### EDA Titulares

Después de la limpieza base, Se analizan los siguientes puntos por país:

- [X] Conteo de duplicados por `conjunto`
- [X] Métricas de longitudes de los titulares (por caractéres y palabras)
- [X] Palabras más repetidas, 1-grama y n-gramas *
- [X] Proporción de dominios
- [X] Nulos por fecha en títulos

Nota.

Conjunto de datos post limpieza base -> https://huggingface.co/datasets/ismaelportog/news_data

Resultados -> PDF Adjunto

### Limpieza

Puntos a tocar

[X] Normalización de los textos: Esto incluye la eliminación de caracteres especiales que no aportan significado en el contexto financiero, la eliminación de espacios y saltos de línea innecesarios, así como la estandarización de todos los textos a minúsculas.

[ ] Truncamiento de los titulares: Se propone acortar los textos a una longitud cercana a la media observada (aproximadamente 12 palabras). Esto tiene como objetivo reducir la variabilidad excesiva sin perder el sentido principal del titular.

[-] Uso de modelos de resumen para titulares extensos: En los casos donde el truncamiento resultaría demasiado agresivo y podría comprometer el contenido informativo, se propone emplear modelos preentrenados capaces de generar resúmenes concisos manteniendo la esencia semántica del titular.

[X] --Traducción de los titulares al inglés: Se contempla el uso del modelo multilingüe preentrenado NLLB-200 (No Language Left Behind, por sus siglas en inglés). En particular, se utilizará la versión destilada con 600,000,000 de parámetros, debido a su balance entre precisión y eficiencia computacional.

[ ] Eliminación de texto plantilla: Con base en el análisis TF-IDF, se identifican y eliminan patrones textuales repetitivos que no aportan información relevante (por ejemplo, nombres de secciones o frases editoriales genéricas).

[X] --Complementación de noticias en fechas faltantes: En especial, se busca completar el conjunto de datos en los periodos donde se detectaron ausencias, particularmente durante el mes de junio de 2025.

[ ] Ingeniería de características temporal: Se ajustan las fechas en función de la hora de publicación. Por ejemplo, si una noticia se publica después de las 16:00 horas, se asigna al día siguiente, dado que su contenido impactaría el precio de apertura del mercado del día posterior.

[X] -- -> En proceso
[-] --> Solución no viable
