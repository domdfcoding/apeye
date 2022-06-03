#  Adapted from https://github.com/john-kurkowski/tldextract
#  Licensed under the BSD 3-Clause License
#
#  Copyright (c) 2020, John Kurkowski
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
#  2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
from ipaddress import IPv4Address

# 3rd party
from apeye_core._tld import extract_tld

# this package
from apeye import Domain


def assert_extract(url, expected_domain_data, expected_ip_data=None):
	(expected_fqdn, expected_subdomain, expected_domain, expected_tld) = expected_domain_data
	ext = Domain._make(extract_tld(url))
	assert expected_fqdn == ext.fqdn
	assert expected_subdomain == ext.subdomain
	assert expected_domain == ext.domain
	assert expected_tld == ext.suffix
	assert expected_ip_data == ext.ipv4


def test_american():
	assert_extract("https://www.google.com", ("www.google.com", "www", "google", "com"))


def test_british():
	assert_extract("https://www.theregister.co.uk", ("www.theregister.co.uk", "www", "theregister", "co.uk"))


def test_no_subdomain():
	assert_extract("https://gmail.com", ("gmail.com", '', "gmail", "com"))


def test_nested_subdomain():
	assert_extract(
			"https://media.forums.theregister.co.uk",
			("media.forums.theregister.co.uk", "media.forums", "theregister", "co.uk")
			)


def test_odd_but_possible():
	assert_extract("https://www.www.com", ("www.www.com", "www", "www", "com"))
	assert_extract("https://www.com", ("www.com", '', "www", "com"))


def test_suffix():
	assert_extract("com", ('', '', '', "com"))
	assert_extract("co.uk", ('', '', '', "co.uk"))


def test_local_host():
	assert_extract("https://internalunlikelyhostname/", ('', '', "internalunlikelyhostname", ''))
	assert_extract("https://internalunlikelyhostname.bizarre", ('', "internalunlikelyhostname", "bizarre", ''))


def test_qualified_local_host():
	assert_extract(
			"https://internalunlikelyhostname.info/",
			("internalunlikelyhostname.info", '', "internalunlikelyhostname", "info")
			)
	assert_extract(
			"https://internalunlikelyhostname.information/", ('', "internalunlikelyhostname", "information", '')
			)


def test_ip():
	assert_extract(
			"https://216.22.0.192/",
			('', '', "216.22.0.192", ''),
			expected_ip_data=IPv4Address("216.22.0.192"),
			)
	assert_extract("https://216.22.project.coop/", ("216.22.project.coop", "216.22", "project", "coop"))


def test_looks_like_ip():
	assert_extract("1é", ('', '', "1é", ''))


def test_punycode():
	assert_extract("https://xn--h1alffa9f.xn--p1ai", ("xn--h1alffa9f.xn--p1ai", '', "xn--h1alffa9f", "xn--p1ai"))
	assert_extract("https://xN--h1alffa9f.xn--p1ai", ("xN--h1alffa9f.xn--p1ai", '', "xN--h1alffa9f", "xn--p1ai"))
	assert_extract("https://XN--h1alffa9f.xn--p1ai", ("XN--h1alffa9f.xn--p1ai", '', "XN--h1alffa9f", "xn--p1ai"))
	# Entries that might generate UnicodeError exception
	# This subdomain generates UnicodeError 'IDNA does not round-trip'
	assert_extract(
			"xn--tub-1m9d15sfkkhsifsbqygyujjrw602gk4li5qqk98aca0w.google.com",
			(
					"xn--tub-1m9d15sfkkhsifsbqygyujjrw602gk4li5qqk98aca0w.google.com",
					"xn--tub-1m9d15sfkkhsifsbqygyujjrw602gk4li5qqk98aca0w",
					"google",
					"com"
					)
			)
	# This subdomain generates UnicodeError 'incomplete punicode string'
	assert_extract(
			"xn--tub-1m9d15sfkkhsifsbqygyujjrw60.google.com",
			(
					"xn--tub-1m9d15sfkkhsifsbqygyujjrw60.google.com",
					"xn--tub-1m9d15sfkkhsifsbqygyujjrw60",
					"google",
					"com"
					)
			)


def test_invalid_puny_with_puny():
	assert_extract(
			"https://xn--zckzap6140b352by.blog.so-net.xn--wcvs22d.hk",
			(
					"xn--zckzap6140b352by.blog.so-net.xn--wcvs22d.hk",
					"xn--zckzap6140b352by.blog",
					"so-net",
					"xn--wcvs22d.hk"
					)
			)
	assert_extract("https://xn--&.so-net.com", ("xn--&.so-net.com", "xn--&", "so-net", "com"))


def test_puny_with_non_puny():
	assert_extract(
			"https://xn--zckzap6140b352by.blog.so-net.教育.hk",
			("xn--zckzap6140b352by.blog.so-net.教育.hk", "xn--zckzap6140b352by.blog", "so-net", "教育.hk")
			)


def test_idna_2008():
	"""Python supports IDNA 2003.
	The IDNA library adds 2008 support for characters like ß.
	"""
	assert_extract("xn--gieen46ers-73a.de", ("xn--gieen46ers-73a.de", '', "xn--gieen46ers-73a", "de"))


def test_empty():
	assert_extract("https://", ('', '', '', ''))


def test_scheme():
	assert_extract("https://mail.google.com/mail", ("mail.google.com", "mail", "google", "com"))
	assert_extract("ssh://mail.google.com/mail", ("mail.google.com", "mail", "google", "com"))
	assert_extract("//mail.google.com/mail", ("mail.google.com", "mail", "google", "com"))
	assert_extract("mail.google.com/mail", ("mail.google.com", "mail", "google", "com"))


def test_port():
	assert_extract("git+ssh://www.github.com:8443/", ("www.github.com", "www", "github", "com"))


def test_username():
	assert_extract("ftp://johndoe:5cr1p7k1dd13@1337.warez.com:2501", ("1337.warez.com", "1337", "warez", "com"))


def test_query_fragment():
	assert_extract("https://google.com?q=cats", ("google.com", '', "google", "com"))
	assert_extract("https://google.com#Welcome", ("google.com", '', "google", "com"))
	assert_extract("https://google.com/#Welcome", ("google.com", '', "google", "com"))
	assert_extract("https://google.com/s#Welcome", ("google.com", '', "google", "com"))
	assert_extract("https://google.com/s?q=cats#Welcome", ("google.com", '', "google", "com"))


def test_regex_order():
	assert_extract("https://www.parliament.uk", ("www.parliament.uk", "www", "parliament", "uk"))
	assert_extract("https://www.parliament.co.uk", ("www.parliament.co.uk", "www", "parliament", "co.uk"))


def test_unhandled_by_iana():
	assert_extract("https://www.cgs.act.edu.au/", ("www.cgs.act.edu.au", "www", "cgs", "act.edu.au"))
	assert_extract("https://www.google.com.au/", ("www.google.com.au", "www", "google", "com.au"))


def test_tld_is_a_website_too():
	assert_extract("https://www.metp.net.cn", ("www.metp.net.cn", "www", "metp", "net.cn"))
	# This is unhandled by the PSL. Or is it?
	# assert_extract(https://www.net.cn', ('www.net.cn', 'www', 'net', 'cn'))


def test_dns_root_label():
	assert_extract("https://www.example.com./", ("www.example.com", "www", "example", "com"))


def test_private_domains():
	assert_extract("https://waiterrant.blogspot.com", ("waiterrant.blogspot.com", "waiterrant", "blogspot", "com"))


def test_ipv4():
	assert_extract(
			"https://127.0.0.1/foo/bar", ('', '', "127.0.0.1", ''), expected_ip_data=IPv4Address("127.0.0.1")
			)


def test_ipv4_bad():
	assert_extract("https://256.256.256.256/foo/bar", ('', "256.256.256", "256", ''))


def test_ipv4_lookalike():
	assert_extract("https://127.0.0.1.9/foo/bar", ('', "127.0.0.1", '9', ''))


def test_result_as_dict():
	result = Domain._make(
			extract_tld("https://admin:password1@www.google.com:666/secret/admin/interface?param1=42")
			)
	expected_dict = {"subdomain": "www", "domain": "google", "suffix": "com"}
	assert result._asdict() == expected_dict
