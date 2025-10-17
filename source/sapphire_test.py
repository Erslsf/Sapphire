
#--------------------Функции отправки (не готово)-----------------------
# def send_usdt_tron(
#     private_key_hex: str,
#     to_address: str,
#     amount: float
# ) -> dict:
#     """
#     Отправляет amount USDT (TRC‑20) на адрес to_address.

#     :param private_key_hex: ваш приватный ключ в hex‑формате (без '0x')
#     :param to_address: адрес получателя (base58, например 'T...')
#     :param amount: количество USDT (с дробной частью)
#     :return: результат broadcast + статус подтверждения
#     """
#     # Проверяем, что сумма положительная
#     if amount <= 0:
#         raise ValueError("Amount must be positive")
#           # Инициализируем клиента Tron и устанавливаем API ключ в заголовках
#     client = Tron(network='mainnet')
#     client.provider.sess.headers['TRON-PRO-API-KEY'] = API_KEY
#     priv_key = PrivateKey(bytes.fromhex(private_key_hex))
    
#     # Переводим float-значение в целое число сатоши токена
#     token_amount = int(amount * 10**6)  # 6 знаков после запятой для USDT
#     usdt_contract = client.get_contract(USDT_CONTRACT)
    
#     # Строим и подписываем транзакцию
#     tx = (
#         usdt_contract.functions.transfer(to_address, token_amount)  # Указываем функцию контракта
#         .with_owner(priv_key.public_key.to_base58check_address())   # Устанавливаем владельца
#         .fee_limit(16_500_000)                                      # Устанавливаем лимит комиссии
#         .build()                                                    # Создаем транзакцию
#         .sign(priv_key)                                             # Подписываем транзакцию
#     )    # Отправляем и ждём включения в блок
#     res = tx.broadcast().wait()
#     # Извлекаем только txid из ответа
#     if isinstance(res, dict) and 'txid' in res and 'id' in res['txid']:
#         return res['txid']['id']
#     return res
# def send_bitcoins(sender_address, recipient_address, sender_priv_key,
#                   amount_btc, fee='normal', witness_type='legacy',
#                   broadcast=False):

#     wallet_name = f"temp_{sender_address[-6:]}"
#     try:
#      wallet_delete(wallet_name, force=True)
#     except WalletError:
#      pass 
#     k = Key(import_key=sender_priv_key, is_private=True, compressed=False, network="bitcoin")
#     # As u can see, i used compressed=False, which is important for my wallet.(if compressed=True, my pub key and address will be different to original one)

#     w = Wallet.create(
#         wallet_name,
#         keys=k,
#         network='bitcoin', 
#         witness_type=witness_type,
#         scheme='single'
#     )
#     try:
#         w.utxos_delete()
#     except Exception:
#         pass
#     w.providers = ['blockchaininfo']
#     w.utxos_update() 
#     w.utxos()
#     tx = w.send_to(recipient_address,
#                    int(amount_btc * 1e8),  
#                    fee=fee,
#                    replace_by_fee=True,
#                    broadcast=broadcast)

#     raw_hex = tx.raw_hex()
#     url = "https://mempool.space/api/tx"
#     resp = requests.post(
#     url,
#     data=raw_hex,        # важно передать именно байты hex‑строки
#     )
#     if not tx.verify():
#         print("Ошибка верификации подписи!")
#         print(tx.errors)
#         exit()
#     else:
#         print("✔ Подпись успешно проверена!")
#     if resp.ok:
#         txid = resp.text.strip()
#         print("✔ Транзакция принята, txid =", txid)
#         wallet_delete(wallet_name, force=True)
#         return {"txid": txid}
#     else:
#         wallet_delete(wallet_name, force=True)
#         print(f"❌ {url} вернул ошибку {resp.status_code}, пробуем следующий…")
#         print(resp.text)
#-----------------------------------------------------------