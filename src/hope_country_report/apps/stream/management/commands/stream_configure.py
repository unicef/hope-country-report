from django.core.management.base import BaseCommand, CommandError
from streaming.backends import get_backend
from streaming.backends.rabbitmq import RabbitMQBackend
from streaming.exceptions import AuthorizationError, StreamingConfigError


class Command(BaseCommand):
    help = "Configures exchanges, queues, and bindings for django-streaming."

    def handle(self, *args, **options):
        from hope_country_report.apps.stream.models import Event

        self.stdout.write("Setting up streaming infrastructure from Event models...")

        backend = get_backend()
        if not isinstance(backend, RabbitMQBackend):
            raise CommandError("This command only supports the RabbitMQ backend.")

        try:
            backend.connect(raise_if_error=True)

            exchange_name = "django-streaming-broadcast"

            self.stdout.write(f"Configuring main exchange '{exchange_name}'...")
            alternate_exchange_name = f"{exchange_name}_unrouted"
            backend.channel.exchange_declare(exchange=alternate_exchange_name, exchange_type="fanout", durable=True)
            unrouted_queue_name = f"{exchange_name}_unrouted_queue"
            backend.channel.queue_declare(queue=unrouted_queue_name, durable=True)
            backend.channel.queue_bind(queue=unrouted_queue_name, exchange=alternate_exchange_name)
            backend.channel.exchange_declare(
                exchange=exchange_name,
                exchange_type="topic",
                durable=True,
                arguments={"alternate-exchange": alternate_exchange_name},
            )

            self.stdout.write("Configuring queues and bindings from database Events...")
            events = Event.objects.filter(enabled=True).select_related("office")
            if not events:
                self.stdout.write(
                    self.style.WARNING("No enabled Event models found in the database. No queues configured.")
                )

            for event in events:
                if not event.office:
                    self.stdout.write(
                        self.style.WARNING(f"Skipping event '{event.name}' because it has no associated office.")
                    )
                    continue

                office_code = event.office.code.lower()
                queue_name = f"queue_hcr_{office_code}"
                routing_key_pattern = f"hcr.{office_code}.*"

                self.stdout.write(f"  - Declaring queue '{queue_name}'")
                backend.channel.queue_declare(queue=queue_name, durable=True)

                self.stdout.write(
                    f"  - Binding queue '{queue_name}' to exchange '{exchange_name}' with key '{routing_key_pattern}'"
                )
                backend.channel.queue_bind(queue=queue_name, exchange=exchange_name, routing_key=routing_key_pattern)

            self.stdout.write(self.style.SUCCESS("Successfully configured streaming infrastructure."))

        except (StreamingConfigError, AuthorizationError) as e:
            raise CommandError(f"Failed to configure streaming infrastructure: {e}")
        finally:
            if backend and getattr(backend, "_connection", None) and backend._connection.is_open:
                backend.disconnect()
