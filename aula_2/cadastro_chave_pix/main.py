from app import criarApp


if __name__ == "__main__":
    app = criarApp()
    app.run(host="127.0.0.1", port=5000, debug=True)

