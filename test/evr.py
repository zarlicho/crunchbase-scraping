for x in range(3):
    try:
        print(2/0)
        break
    except Exception as e:
        print(f"{e} in {x}x")