import pandas as pd
import aiohttp
import asyncio
import tkinter as tk
from tkinter import messagebox

# Лимит одновременных задач для ускорения и предотвращения перегрузки
MAX_CONCURRENT_TASKS = 5

# Загрузка данных из Excel
def load_data(filename):
    try:
        df = pd.read_excel(filename)
        return df.set_index('Domain').to_dict('index')
    except Exception as e:
        messagebox.showerror("Ошибка загрузки файла", f"Ошибка при загрузке данных из {filename}: {e}")
        return {}

# Асинхронная функция для изменения настроек на Cloudflare
async def change_setting(session, domain, setting, enable, credentials, semaphore):
    async with semaphore:  # Ограничение количества одновременных задач
        api_token = credentials.get('API_Token')
        zone_id = credentials.get('Zone_ID')
        email = credentials.get('Email')

        if not api_token or not zone_id:
            print(f"Отсутствуют данные API_Token или Zone_ID для домена {domain}")
            return False

        headers = {
            'Authorization': f'Bearer {api_token}' if api_token and not email else None,
            'X-Auth-Email': email if email else None,
            'X-Auth-Key': api_token if api_token and email else None,
            'Content-Type': 'application/json'
        }
        headers = {k: v for k, v in headers.items() if v is not None}

        setting_urls = {
            "ipv6": f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/ipv6",
            "always_use_https": f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/always_use_https",
            "tls_1_3": f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/tls_1_3",
            "under_attack": f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/security_level"
        }
        url = setting_urls.get(setting)
        if not url:
            print(f"Неизвестная настройка: {setting}")
            return False

        data = {
            "value": "under_attack" if enable and setting == "under_attack" else "medium" if setting == "under_attack" else "on" if enable else "off"
        }

        async with session.patch(url, headers=headers, json=data) as response:
            if response.status == 200:
                print(f"Настройка {setting} для домена {domain} успешно {'включена' if enable else 'отключена'}.")
                return True
            else:
                print(f"Ошибка при изменении настройки {setting} для домена {domain}: {await response.text()}")
                return False

# Асинхронная функция для очистки кеша
async def purge_cache(session, domain, credentials, semaphore):
    async with semaphore:
        api_token = credentials.get('API_Token')
        zone_id = credentials.get('Zone_ID')
        email = credentials.get('Email')

        if not api_token or not zone_id:
            print(f"Отсутствуют данные API_Token или Zone_ID для домена {domain}")
            return False

        headers = {
            'Authorization': f'Bearer {api_token}' if api_token and not email else None,
            'X-Auth-Email': email if email else None,
            'X-Auth-Key': api_token if api_token and email else None,
            'Content-Type': 'application/json'
        }
        headers = {k: v for k, v in headers.items() if v is not None}

        url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache"
        data = {"purge_everything": True}

        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                print(f"Кеш для домена {domain} успешно очищен.")
                return True
            else:
                print(f"Ошибка при очистке кеша для домена {domain}: {await response.text()}")
                return False

# Асинхронная функция для применения всех настроек и очистки кеша для каждого домена
async def apply_all_changes(domains, ipv6_status, https_status, tls_status, attack_mode, purge_cache_var,
                            progress_label):
    data = load_data('cloudflare_accounts.xlsx')
    if not data:
        messagebox.showerror("Ошибка", "Не удалось загрузить данные из файла.")
        return

    # Словарь для хранения сессий по каждому аккаунту (API Token)
    sessions = {}
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_TASKS)
    all_results = []

    try:
        for domain in domains:
            if domain in data:
                credentials = data[domain]
                api_token = credentials.get('API_Token')

                # Используем разные сессии для разных API токенов
                if api_token not in sessions:
                    sessions[api_token] = aiohttp.ClientSession()

                session = sessions[api_token]

                # Запуск задач для домена
                tasks = []

                if ipv6_status['apply'].get():
                    tasks.append(change_setting(session, domain, "ipv6", ipv6_status['state'].get() == "on", credentials, semaphore))
                if https_status['apply'].get():
                    tasks.append(change_setting(session, domain, "always_use_https", https_status['state'].get() == "on", credentials, semaphore))
                if tls_status['apply'].get():
                    tasks.append(change_setting(session, domain, "tls_1_3", tls_status['state'].get() == "on", credentials, semaphore))
                if attack_mode['apply'].get():
                    tasks.append(change_setting(session, domain, "under_attack", attack_mode['state'].get() == "on", credentials, semaphore))

                # Выполнение всех задач параллельно для одного домена
                results = await asyncio.gather(*tasks)

                # Очистка кэша после настроек
                if purge_cache_var['apply'].get():
                    cache_result = await purge_cache(session, domain, credentials, semaphore)
                    results.append(cache_result)

                # Обновление прогресса
                success = all(results)
                all_results.append(f"{domain}: {'успешно' if success else 'не удалось'}")
                progress_label.config(text="\n".join(all_results))
                progress_label.update()
    finally:
        # Закрываем все сессии после завершения всех задач
        await asyncio.gather(*(session.close() for session in sessions.values()))

    # Финальный отчет
    progress_label.config(text="Все операции выполнены.")
    progress_label.update()
    messagebox.showinfo("Результаты выполнения", "\n".join(all_results))


# Функция для переключения тумблеров
def toggle_setting(setting_var, button, on_text, off_text):
    setting_var.set("on" if setting_var.get() == "off" else "off")
    button.config(text=on_text if setting_var.get() == "on" else off_text,
                  bg="green" if setting_var.get() == "on" else "red")

# Создание интерфейса
def create_interface():
    window = tk.Tk()
    window.title("Cloudflare Settings Manager")
    window.geometry("500x600")

    tk.Label(window, text="Введите домены (каждый с новой строки):").pack()
    domains_text = tk.Text(window, width=60, height=10)
    domains_text.pack()

    def get_domains():
        domains = domains_text.get("1.0", tk.END).strip().splitlines()
        return [d.strip() for d in domains if d.strip()]

    # Переменные для состояний тумблеров и чекбоксов
    ipv6_status = {'state': tk.StringVar(value="off"), 'apply': tk.BooleanVar()}
    https_status = {'state': tk.StringVar(value="off"), 'apply': tk.BooleanVar()}
    tls_status = {'state': tk.StringVar(value="off"), 'apply': tk.BooleanVar()}
    attack_mode = {'state': tk.StringVar(value="off"), 'apply': tk.BooleanVar()}
    purge_cache_var = {'state': tk.StringVar(value="off"), 'apply': tk.BooleanVar()}

    # Функция для создания тумблеров и чекбоксов
    def create_toggle(frame, label_text, setting_var, apply_var):
        toggle_button = tk.Button(
            frame, text=f"{label_text} Выкл", bg="red", fg="white", width=20,
            command=lambda: toggle_setting(setting_var, toggle_button, f"{label_text} Вкл", f"{label_text} Выкл")
        )
        toggle_button.pack(side="left")

        apply_checkbox = tk.Checkbutton(frame, text="Применить", variable=apply_var)
        apply_checkbox.pack(side="right")

    # Чекбокс "Выбрать все"
    def toggle_all_checkboxes():
        state = select_all_var.get()
        ipv6_status['apply'].set(state)
        https_status['apply'].set(state)
        tls_status['apply'].set(state)
        attack_mode['apply'].set(state)
        purge_cache_var['apply'].set(state)

    select_all_var = tk.BooleanVar()
    select_all_checkbox = tk.Checkbutton(window, text="Выбрать все", variable=select_all_var,
                                         command=toggle_all_checkboxes)
    select_all_checkbox.pack(pady=5)

    # Создание фреймов и тумблеров с чекбоксами для каждой опции
    for label, status_var in [("IPv6", ipv6_status),
                              ("Always Use HTTPS", https_status),
                              ("TLS 1.3", tls_status),
                              ("Under Attack Mode", attack_mode)]:
        frame = tk.Frame(window)
        frame.pack(pady=5)
        create_toggle(frame, label, status_var['state'], status_var['apply'])

    # Чекбокс для очистки кеша
    purge_cache_checkbox = tk.Checkbutton(window, text="Очистить кеш", variable=purge_cache_var['apply'])
    purge_cache_checkbox.pack(pady=5)

    # Метка для отображения прогресса
    progress_label = tk.Label(window, text="Прогресс выполнения: 0%")
    progress_label.pack(pady=10)

    # Кнопка для применения всех выбранных изменений
    def on_apply_all():
        domains = get_domains()
        if not domains:
            messagebox.showwarning("Ошибка", "Введите хотя бы один домен.")
            return
        asyncio.run(apply_all_changes(domains, ipv6_status, https_status, tls_status, attack_mode, purge_cache_var,
                                      progress_label))

    apply_button = tk.Button(window, text="Применить выбранное", command=on_apply_all, width=20)
    apply_button.pack(pady=20)

    window.mainloop()

create_interface()
