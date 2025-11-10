from csv import reader

from dotenv import load_dotenv
from openai import OpenAI

from prisma import Prisma

load_dotenv()

# docker run --name vectorchord-db -e POSTGRES_PASSWORD=postgres -p 5432:5432 --volume ./data:/var/lib/postgresql/data -d tensorchord/vchord-postgres:pg17-v0.5.3


def get_descriptions():
    with open("/home/mmk21/Downloads/descriptions.csv", "r") as read_obj:
        csv_reader = reader(read_obj)
        descriptions = [record[0] for record in csv_reader]
    return descriptions


async def add_embeddings_to_db(descriptions):
    client = OpenAI()
    prisma = Prisma()
    await prisma.connect()

    for desc in descriptions:
        print(desc)
        response = client.embeddings.create(input=desc, model="text-embedding-3-large")
        print(response.data[0].embedding)
        await prisma.execute_raw(
            """
            INSERT INTO "Ticket" ("description", "textEmbedding")
            VALUES ($1, $2);
            """,
            desc,
            response.data[0].embedding,
        )


async def main():
    descriptions = get_descriptions()
    relevant_descriptions = descriptions[-3:]
    await add_embeddings_to_db(relevant_descriptions)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
