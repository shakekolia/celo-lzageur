import json
import time
import random
from web3 import Web3
from web3.auto import w3
from web3.middleware import geth_poa_middleware
from eth_account import Account

# Конфигурация RPC и chainID
rpc_url = "https://forno.celo.org"  # Замените на свой собственный RPC URL
chain_id = 42220  # Замените на соответствующий chainID для сети CELO

# Подключение к сети CELO
w3 = Web3(Web3.HTTPProvider(rpc_url))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Дополнительный middleware для CELO

# Адрес контракта токена LZ-agEUR
contract_address = "0xf1dDcACA7D17f8030Ab2eb54f2D9811365EFe123"  # Замените на адрес вашего контракта

# Функция для проверки баланса токена
def check_token_balance(wallet_address, contract_address):
    contract = w3.eth.contract(contract_address, abi=abi)
    balance = contract.functions.balanceOf(wallet_address).call()
    return balance

# Функция для отправки транзакции
def send_transaction(wallet, contract_address, amount):
    gas_limit = w3.eth.estimate_gas({
        'from': wallet[0],
        'to': contract_address,
        'data': f'0x00f714ce{amount:064x}000000000000000000000000{wallet[0][2:]}'
    })

    gas_price = w3.eth.gas_price
    nonce = w3.eth.get_transaction_count(wallet[0])

    transaction = {
        'to': contract_address,
        'value': 0,
        'gas': gas_limit,
        'gasPrice': gas_price,
        'nonce': nonce,
        'data': f'0x00f714ce{amount:064x}000000000000000000000000{wallet[0][2:]}'
    }

    signed_txn = w3.eth.account.sign_transaction(transaction, private_key=wallet[1])
    try:
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return tx_hash
    except Exception as e:
        print(f"Ошибка при отправке транзакции: {str(e)}")
        return None

# Загрузка ABI контракта
with open('erc20.json', 'r') as f:
    abi = json.load(f)

# Загрузка приватных ключей из файла и перемешивание кошельков
with open('private.txt', 'r') as f:
    private_keys = f.read().splitlines()
random.shuffle(private_keys)

# Количество кошельков, которые будут обработаны
num_wallets = len(private_keys)
print(f"Количество кошельков для обработки: {num_wallets}")

# Итерация по приватным ключам
for private_key in private_keys:
    # Получение адреса кошелька из приватного ключа
    wallet_address = w3.eth.account.from_key(private_key).address

    # Проверка баланса токена
    token_balance = check_token_balance(wallet_address, contract_address)
    print(f"Баланс токена на кошельке {wallet_address}: {token_balance}")

    if token_balance > 0:
        # Отправка транзакции
        transaction_hash = send_transaction((wallet_address, private_key), contract_address, token_balance)
        if transaction_hash:
            print(f"Транзакция отправлена. Hash транзакции: {transaction_hash.hex()}")
            print(f"Сумма отправленных токенов: {token_balance}")
        else:
            print("Ошибка при отправке транзакции.")

    # Задержка в указанном диапазоне времени (например, 30-100 секунд)
    delay = random.randint(30, 100)
    time.sleep(delay)
