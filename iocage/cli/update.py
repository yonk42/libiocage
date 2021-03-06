# Copyright (c) 2014-2017, iocage
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted providing that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""start module for the cli."""
import click

import iocage.lib.errors
import iocage.lib.Jails
import iocage.lib.Logger
import iocage.lib.Config.Jail.File.Fstab

__rootcmd__ = True


@click.command(name="start", help="Starts the specified jails or ALL.")
@click.pass_context
@click.argument("jails", nargs=-1)
def cli(ctx, jails):
    """
    Update Jails
    """
    logger = ctx.parent.logger
    print_function = ctx.parent.print_events

    if len(jails) == 0:
        logger.error("No jail selector provided")
        exit(1)

    zfs = iocage.lib.ZFS.ZFS()
    zfs.logger = logger
    host = iocage.lib.Host.Host(logger=logger, zfs=zfs)

    filters = jails + ("template=no",)
    jails = iocage.lib.Jails.JailsGenerator(
        logger=logger,
        host=host,
        zfs=zfs,
        filters=filters
    )

    changed_jails = []
    failed_jails = []
    for jail in jails:
        try:
            changed = print_function(jail.updater.apply())
            if changed is True:
                changed_jails.append(jail)
        except iocage.lib.errors.UpdateFailure:
            failed_jails.append(jail)

    if len(failed_jails) > 0:
        return False

    if len(changed_jails) == 0:
        jails_input = " ".join(list(jails))
        logger.error(
            f"No jail was updated or matched your input: {jails_input}"
        )
        return False

    return True
