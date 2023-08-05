# libpythonpro
Módulo para exemplificar construção de projetos Python no curso PyTools

Nesse curso é ensinado como contribuir com projetos de código aberto

Link para o curso [Python Pro](https://www.python.pro.br/)

[![Build Status](https://travis-ci.org/DiksonSantos/LibPythonPRO.svg?branch=main)](https://travis-ci.org/DiksonSantos/LibPythonPRO)

Suportada versão 3 de Python

Para instalar:

```console
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Para conferir qualidade de código:

```console
flake8

```

Tópicos a serem abordados:
 1. Git
 2. Virtualenv
 3. Pip


"""
Para instalar o conteudo\dependencias Listadas em Requirements.TXT, use o 
seguinte comando:

pip install -r requirements.txt

Ou o endereço de onde se encontra o requirements.txt

Com isso não precisamos manadar o conteudo da pasta .venv (Que contem as 
dependencias) para o GitHyb, mas mandamos só o requirements.txt que tem o
nome de todas as dependencias que o projeto necessita para rodar.

A linha:

-r requirements.txt

Dentro de requirements_c_flake8.txt   -> Faz com que o conteudo de requirements.txt
seja também instalado, se o requirements_c_flake8.txt for instalado com o
comando   pip install -r requirements_c_flake8.txt
"""
