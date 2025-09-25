# Phone Call Service
Сервис для управления телефонными звонками, загрузки аудиозаписей, их обработки и хранения. Поддерживает автоматическую транскрипцию, обнаружение тишины и предоставление временных ссылок на запись.

## 📦 Требования
- Docker и Docker Compose
- Достаточно свободного места на диске (~3 ГБ)

## 🚀 Быстрый старт
Склонируйте репозиторий:
```bash
git clone https://github.com/SynKolbasyn/phone_task.git
cd phone_task
```

Создайте .env из шаблона:

```bash
cp template.env .env
```
При необходимости отредактируйте значения в .env.

Запустите сервисы:
```bash
docker compose up --build --pull always -d
```

При первом запуске будут собраны образы, инициализированы база данных, `MinIO`, `Celery`, `Postgres`, `Nginx` и другие компоненты.

Доступные эндпоинты:
- API: [`https://localhost/docs`](https://localhost/docs) (FastAPI)
- Grafana (логи): [`https://grafana.localhost`](https://grafana.localhost)
- Health-check: [`GET /health`](https://localhost/health)

### ⚠️ Сертификаты самоподписанные — браузер может предупреждать о безопасности. Продолжите вручную или добавьте исключение. 

## 📊 Мониторинг и логи
Все логи (`nginx`, `fastapi`) отправляются в `Loki` через `Grafana Alloy`.
Панель мониторинга доступна в Grafana:
URL: [`https://grafana.localhost`](https://grafana.localhost)
Анонимный доступ включен с правами администратора (только для dev-среды).

## 🔐 Безопасность
Для продакшена обязательно замените:
- .env значения (особенно пароли и ключи)
- SSL-сертификаты в nginx/ и minio/
- Отключите анонимный доступ в Grafana

## 📄 Лицензия
Проект распространяется под лицензией AGPL-3.0-or-later. Подробнее см. в файле [`LICENSE`](LICENSE).

## 📬 Контакты
- Разработчик: `Andrew Kozmin`
- Email: `syn.kolbasyn.06@gmail.com`
