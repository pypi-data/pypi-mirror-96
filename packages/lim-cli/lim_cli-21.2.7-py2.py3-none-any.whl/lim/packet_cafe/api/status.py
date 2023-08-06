# -*- coding: utf-8 -*-

import argparse
import logging
import textwrap

from cliff.lister import Lister
from lim.packet_cafe import add_packet_cafe_global_options
from lim.packet_cafe import get_packet_cafe
from lim.packet_cafe import NO_SESSIONS_MSG

logger = logging.getLogger(__name__)


class Status(Lister):
    """Return the status of all tools for a session and request ID."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.add_argument('sess_id', nargs='?', default=None)
        parser.add_argument('req_id', nargs='?', default=None)
        parser.epilog = textwrap.dedent("""
            Return the status of all tools for a session and request ID.

            By default, the last session ID and request ID (if available)
            are used.

            ::

                $ lim cafe status
                [+] implicitly reusing last session id bae5d69c-7180-445d-a8db-22a5ef0872e8
                [+] implicitly reusing last request id c33c56abe4c743a8b77e0b76d9548c06
                +---------------+----------+----------------------------------+
                | Tool          | State    | Timestamp                        |
                +---------------+----------+----------------------------------+
                | snort         | Complete | 2020-05-15T01:25:52.669640+00:00 |
                | networkml     | Complete | 2020-05-15T01:26:36.616426+00:00 |
                | pcap-splitter | Complete | 2020-05-15T01:25:56.362483+00:00 |
                | mercury       | Complete | 2020-05-15T01:25:49.773921+00:00 |
                | pcap-dot1q    | Complete | 2020-05-15T01:25:47.988746+00:00 |
                | ncapture      | Complete | 2020-05-15T01:25:46.075214+00:00 |
                | pcapplot      | Complete | 2020-05-15T01:26:24.899752+00:00 |
                | pcap_stats    | Complete | 2020-05-15T01:25:48.251749+00:00 |
                | p0f           | Complete | 2020-05-15T01:26:48.456883+00:00 |
                +---------------+----------+----------------------------------+


            If no session ID is identified, you will be prompted to choose from
            those that are available:

            ::

                $ lim cafe status

                Chose a session:
                  → <CANCEL>
                    57b1484b-5502-4e3c-b6bc-854d4aeb2038
                    57be4843-32c0-4943-93d8-d1ec9bc0e792
                    2d222a53-5b01-4d5e-a659-7da7c21d3cf6
                    73d532d7-3b2b-4a93-9a68-ae7091af6a2f
                    9a949fe6-6520-437f-89ec-e7af6925b1e0
                    7eedfd93-4f65-4422-8d70-a4edf47d7364
                    a42ee6ab-d60b-4d8e-a1df-cb3dc6985c81


            See https://iqtlabs.gitbook.io/packet-cafe/design/api#api-v-1-status-sess_id-req_id
            """)  # noqa
        return add_packet_cafe_global_options(parser)

    def take_action(self, parsed_args):
        logger.debug('[+] showing status for request')
        packet_cafe = get_packet_cafe(self.app, parsed_args)
        ids = packet_cafe.get_session_ids()
        if len(ids) == 0:
            raise RuntimeError(NO_SESSIONS_MSG)
        sess_id = packet_cafe.get_session_id(
            sess_id=parsed_args.sess_id,
            choose=parsed_args.choose
        )
        if sess_id not in ids:
            raise RuntimeError(
                f'[-] session ID { sess_id } not found')
        req_id = packet_cafe.get_request_id(
            req_id=parsed_args.req_id,
            choose=parsed_args.choose
        )
        columns = ['Tool', 'State', 'Timestamp']
        data = []
        status = packet_cafe.get_status(sess_id=sess_id, req_id=req_id)
        if status is None:
            raise RuntimeError('[-] failed to get status for '
                               f'session { sess_id }, '
                               f'request { req_id }')
        for k, v in status.items():
            if type(v) is dict:
                data.append((k, v['state'], v['timestamp']))
        return (columns, data)


# vim: set ts=4 sw=4 tw=0 et :
