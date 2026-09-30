from backend.app.harness.context import limit_context


def test_context_limit():

    test_cases = [
        [],
        [f"Message {i}" for i in range(1, 6)],
        [f"Message {i}" for i in range(1, 11)],
        [f"Message {i}" for i in range(1, 16)]
    ]

    for messages in test_cases:

        result = limit_context(messages)

        print("\n" + "=" * 50)
        print("Original count:", len(messages))
        print("Context count:", len(result))

        for message in result:
            print(message)

        assert len(result) <= 10

        if len(messages) <= 10:
            assert result == messages

        else:
            assert result == messages[-10:]


    print("\nAll context limit tests PASSED")


test_context_limit()