# Глобальные функции для проведения тестов wsqluse


def analyze_response(response):
    # Анализировать ответ функции
    print('Response:', response)
    expected_response = dict
    if type(response) == expected_response:
        print('Test success')
    else:
        print('Test failed. Type:', type(response))
