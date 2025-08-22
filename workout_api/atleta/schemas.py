from typing import Annotated, Optional
from pydantic import UUID4, Field, PositiveFloat

from workoutapi.categorias.schemas import CategoriaIn
from workoutapi.centro_treinamento.schemas import CentroTreinamentoAtleta
from workoutapi.contrib.schemas import BaseSchema, OutMixin


class Atleta(BaseSchema):
    nome: Annotated[
        str,
        Field(description="Nome completo do atleta", example="Joao", max_length=50),
    ]
    cpf: Annotated[
        str,
        Field(description="CPF do atleta", example="123.456.789-00", max_length=14),
    ]
    idade: Annotated[int, Field(description="Idade do atleta", example=25)]
    peso: Annotated[
        PositiveFloat, Field(description="Peso do atleta em kg", example=70.5)
    ]
    altura: Annotated[
        PositiveFloat, Field(description="Altura do atleta em metros", example=1.75)
    ]
    sexo: Annotated[str, Field(description="Sexo do atleta", example="M", max_length=1)]
    categoria: Annotated[CategoriaIn, Field(description="Categoria do Atleta")]
    centro_treinamento: Annotated[
        CentroTreinamentoAtleta, Field(description="Centro de Treinamento do Atleta")
    ]


class AtletaIn(Atleta):
    pass


class AtletaOut(Atleta, OutMixin):
    pass


class AtletaUpdate(BaseSchema):
    nome: Annotated[
        Optional[str],
        Field(
            None, description="Nome completo do atleta", example="Joao", max_length=50
        ),
    ]
    idade: Annotated[
        Optional[int], Field(None, description="Idade do atleta", example=25)
    ]
