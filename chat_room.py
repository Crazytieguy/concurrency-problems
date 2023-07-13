from asyncio import StreamReader, StreamWriter, run, start_server, gather


USERS = set()
WRITERS: dict[str, StreamWriter] = {}


async def handle_connection(reader: StreamReader, writer: StreamWriter):
    print("Accepted connection")
    message = await reader.readline()
    if not message.startswith(b"register "):
        writer.write(
            b"Please start off the conversation with the "
            b"'register <user_name>' command\n"
        )
        writer.close()
        await writer.wait_closed()
        return
    user_name = message.removeprefix(b"register ").decode()
    if user_name in USERS:
        writer.write(b"Please choose a different user name\n")
        writer.close()
        await writer.wait_closed()
        return
    USERS.add(user_name)
    WRITERS[user_name] = writer
    writer.write(f"Connected as {user_name}\n".encode())
    try:
        while True:
            await handle_message(reader, writer, user_name)
    except ConnectionResetError:
        USERS.remove(user_name)
        del WRITERS[user_name]
        for w in WRITERS.values():
            w.write(f"{user_name} disconnected\n".encode())
        await gather(*[w.drain() for w in WRITERS.values()])
        print(f"{user_name} disconnected")


async def handle_message(reader: StreamReader, writer: StreamWriter, user_name: str):
    message = await reader.readline()
    if message == b"":
        raise ConnectionResetError
    match message.decode().strip():
        case "list":
            writer.write(f"users: {', '.join(USERS)}\n".encode())
            await writer.drain()
        case payload:
            payload_to_write = f"{user_name}: {payload}\n".encode()
            for name, w in WRITERS.items():
                if name == user_name:
                    continue
                w.write(payload_to_write)
            await gather(*[w.drain() for w in WRITERS.values()])


async def main():
    server = await start_server(handle_connection, "localhost", 5000)
    await server.serve_forever()


if __name__ == "__main__":
    run(main())
