# Copyright (C) Raffaele Salmaso <raffaele@salmaso.org>
# Copyright (C) 2009-2023, Kyle Fuller and Mariusz Felisiak
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

from datetime import timedelta

from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from metrics.models import Request

DURATION_OPTIONS = {
    "hours": lambda amount: timezone.now() - timedelta(hours=amount),
    "days": lambda amount: timezone.now() - timedelta(days=amount),
    "weeks": lambda amount: timezone.now() - timedelta(weeks=amount),
    "months": lambda amount: timezone.now() + relativedelta(months=-amount),
    "years": lambda amount: timezone.now() + relativedelta(years=-amount),
}


class Command(BaseCommand):
    help = "Purge old requests."

    def add_arguments(self, parser):
        parser.add_argument("amount", type=int)
        parser.add_argument("duration")
        parser.add_argument(
            "--noinput",
            action="store_false",
            dest="interactive",
            default=True,
            help="Tells Django to NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        amount = options["amount"]
        duration = options["duration"]

        # Check we have the correct values
        if duration[-1] != "s":  # If its not plural, make it plural
            duration_plural = "{0}s".format(duration)
        else:
            duration_plural = duration

        if duration_plural not in DURATION_OPTIONS:
            raise CommandError("Amount must be {0}".format(", ".join(DURATION_OPTIONS)))

        qs = Request.objects.filter(timestamp__lte=DURATION_OPTIONS[duration_plural](amount))
        count = qs.count()

        if count == 0:
            self.stdout.write("There are no requests to delete.")
            return

        if options.get("interactive"):
            confirm = input(
                """
You have requested a database reset.
This will IRREVERSIBLY DESTROY any
requests created before {0} {1} ago.
That is a total of {2} requests.
Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel:""".format(
                    amount, duration, count
                )
            )
        else:
            confirm = "yes"

        if confirm == "yes":
            qs.delete()
        else:
            self.stdout.write("Purge cancelled")
