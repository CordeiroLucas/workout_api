from datetime import datetime
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from workoutapi.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from workoutapi.atleta.models import AtletaModel
from workoutapi.categorias.models import CategoriaModel
from workoutapi.centro_treinamento.models import CentroTreinamentoModel
from workoutapi.contrib.dependencies import DatabaseDependency

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select


router = APIRouter()


@router.post(
    "/",
    summary="Criar um novo Atleta",
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut,
)
async def post(
    db_session: DatabaseDependency, atleta_in: AtletaIn = Body(...)
) -> AtletaOut:
    nome_categoria = atleta_in.categoria.nome
    nome_ct = atleta_in.centro_treinamento.nome

    categoria = (
        (
            await db_session.execute(
                select(CategoriaModel).filter_by(nome=nome_categoria)
            )
        )
        .scalars()
        .first()
    )

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A categoria {nome_categoria} não foi encontrada.",
        )

    centro_treinamento = (
        (
            await db_session.execute(
                select(CentroTreinamentoModel).filter_by(nome=nome_ct)
            )
        )
        .scalars()
        .first()
    )

    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"O CT {nome_ct} não foi encontrado.",
        )

    atleta_out = AtletaOut(
        id=uuid4(), created_at=datetime.now(), **atleta_in.model_dump()
    )
    atleta_model = AtletaModel(
        **atleta_out.model_dump(exclude={"categoria", "centro_treinamento"})
    )
    try:
        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id

        db_session.add(atleta_model)
        await db_session.commit()
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro de integridade ao inserir os dados no banco\n{e}",
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro no banco de dados!",
        )

    return atleta_out


@router.get(
    "/",
    summary="Consultar todos os Atletas",
    status_code=status.HTTP_200_OK,
    response_model=list[AtletaOut],
)
async def query(db_session: DatabaseDependency) -> list[AtletaOut]:
    atletas: list[AtletaOut] = (
        (await db_session.execute(select(AtletaModel))).scalars().all()
    )
    return atletas


@router.get(
    "/{id}",
    summary="Consultar uma Atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> AtletaOut:
    atleta_out: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrada no id = {id}",
        )
    return atleta_out


@router.patch(
    "/{id}",
    summary="Editar uma Atleta pelo id",
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def get(
    id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)
) -> AtletaOut:
    atleta_out: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrada no id = {id}",
        )
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta_out, key, value)
    await db_session.commit()
    await db_session.refresh(atleta_out)
    return atleta_out


@router.delete(
    "/{id}",
    summary="Editar uma Atleta pelo id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta: AtletaOut = (
        (await db_session.execute(select(AtletaModel).filter_by(id=id)))
        .scalars()
        .first()
    )

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Atleta não encontrada no id = {id}",
        )

    await db_session.delete(atleta)
    await db_session.commit()
