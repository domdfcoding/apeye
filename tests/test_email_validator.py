# stdlib
import json
import sys

# 3rd party
import pytest
from coincidence import AdvancedFileRegressionFixture
from coincidence.params import param
from domdf_python_tools.compat import PYPY36

# this package
from apeye.email_validator import EmailSyntaxError, ValidatedEmail
from apeye.email_validator import main as validator_main
from apeye.email_validator import validate_email


@pytest.mark.parametrize(
		"email_input,output",
		[
				(
						"Abc@example.com",
						ValidatedEmail(
								local_part="Abc",
								ascii_local_part="Abc",
								smtputf8=False,
								ascii_domain="example.com",
								domain="example.com",
								email="Abc@example.com",
								original_email="Abc@example.com",
								ascii_email="Abc@example.com",
								),
						),
				(
						b"Abc@example.com",
						ValidatedEmail(
								local_part="Abc",
								ascii_local_part="Abc",
								smtputf8=False,
								ascii_domain="example.com",
								domain="example.com",
								email="Abc@example.com",
								original_email="Abc@example.com",
								ascii_email="Abc@example.com",
								),
						),
				(
						"Abc.123@example.com",
						ValidatedEmail(
								local_part="Abc.123",
								ascii_local_part="Abc.123",
								smtputf8=False,
								ascii_domain="example.com",
								domain="example.com",
								email="Abc.123@example.com",
								original_email="Abc.123@example.com",
								ascii_email="Abc.123@example.com",
								),
						),
				(
						b"Abc.123@example.com",
						ValidatedEmail(
								local_part="Abc.123",
								ascii_local_part="Abc.123",
								smtputf8=False,
								ascii_domain="example.com",
								domain="example.com",
								email="Abc.123@example.com",
								original_email="Abc.123@example.com",
								ascii_email="Abc.123@example.com",
								),
						),
				(
						"user+mailbox/department=shipping@example.com",
						ValidatedEmail(
								local_part="user+mailbox/department=shipping",
								ascii_local_part="user+mailbox/department=shipping",
								smtputf8=False,
								ascii_domain="example.com",
								domain="example.com",
								email="user+mailbox/department=shipping@example.com",
								original_email="user+mailbox/department=shipping@example.com",
								ascii_email="user+mailbox/department=shipping@example.com",
								),
						),
				(
						b"user+mailbox/department=shipping@example.com",
						ValidatedEmail(
								local_part="user+mailbox/department=shipping",
								ascii_local_part="user+mailbox/department=shipping",
								smtputf8=False,
								ascii_domain="example.com",
								domain="example.com",
								email="user+mailbox/department=shipping@example.com",
								original_email="user+mailbox/department=shipping@example.com",
								ascii_email="user+mailbox/department=shipping@example.com",
								),
						),
				(
						"!#$%&'*+-/=?^_`.{|}~@example.com",
						ValidatedEmail(
								local_part="!#$%&'*+-/=?^_`.{|}~",
								ascii_local_part="!#$%&'*+-/=?^_`.{|}~",
								smtputf8=False,
								ascii_domain="example.com",
								domain="example.com",
								email="!#$%&'*+-/=?^_`.{|}~@example.com",
								original_email="!#$%&'*+-/=?^_`.{|}~@example.com",
								ascii_email="!#$%&'*+-/=?^_`.{|}~@example.com",
								),
						),
				(
						"伊昭傑@郵件.商務",
						ValidatedEmail(
								local_part="伊昭傑",
								smtputf8=True,
								ascii_domain="xn--5nqv22n.xn--lhr59c",
								domain="郵件.商務",
								email="伊昭傑@郵件.商務",
								original_email="伊昭傑@郵件.商務",
								),
						),
				(
						"राम@मोहन.ईन्फो",
						ValidatedEmail(
								local_part="राम",
								smtputf8=True,
								ascii_domain="xn--l2bl7a9d.xn--o1b8dj2ki",
								domain="मोहन.ईन्फो",
								email="राम@मोहन.ईन्फो",
								original_email="राम@मोहन.ईन्फो",
								),
						),
				(
						"юзер@екзампл.ком",
						ValidatedEmail(
								local_part="юзер",
								smtputf8=True,
								ascii_domain="xn--80ajglhfv.xn--j1aef",
								domain="екзампл.ком",
								email="юзер@екзампл.ком",
								original_email="юзер@екзампл.ком",
								),
						),
				(
						"θσερ@εχαμπλε.ψομ",
						ValidatedEmail(
								local_part="θσερ",
								smtputf8=True,
								ascii_domain="xn--mxahbxey0c.xn--xxaf0a",
								domain="εχαμπλε.ψομ",
								email="θσερ@εχαμπλε.ψομ",
								original_email="θσερ@εχαμπλε.ψομ",
								),
						),
				(
						"葉士豪@臺網中心.tw",
						ValidatedEmail(
								local_part="葉士豪",
								smtputf8=True,
								ascii_domain="xn--fiqq24b10vi0d.tw",
								domain="臺網中心.tw",
								email="葉士豪@臺網中心.tw",
								original_email="葉士豪@臺網中心.tw",
								),
						),
				(
						"jeff@臺網中心.tw",
						ValidatedEmail(
								local_part="jeff",
								ascii_local_part="jeff",
								smtputf8=False,
								ascii_domain="xn--fiqq24b10vi0d.tw",
								domain="臺網中心.tw",
								email="jeff@臺網中心.tw",
								original_email="jeff@臺網中心.tw",
								ascii_email="jeff@xn--fiqq24b10vi0d.tw",
								),
						),
				(
						"葉士豪@臺網中心.台灣",
						ValidatedEmail(
								local_part="葉士豪",
								smtputf8=True,
								ascii_domain="xn--fiqq24b10vi0d.xn--kpry57d",
								domain="臺網中心.台灣",
								email="葉士豪@臺網中心.台灣",
								original_email="葉士豪@臺網中心.台灣",
								),
						),
				(
						"jeff葉@臺網中心.tw",
						ValidatedEmail(
								local_part="jeff葉",
								smtputf8=True,
								ascii_domain="xn--fiqq24b10vi0d.tw",
								domain="臺網中心.tw",
								email="jeff葉@臺網中心.tw",
								original_email="jeff葉@臺網中心.tw",
								),
						),
				(
						"ñoñó@example.com",
						ValidatedEmail(
								local_part="ñoñó",
								smtputf8=True,
								ascii_domain="example.com",
								domain="example.com",
								email="ñoñó@example.com",
								original_email="ñoñó@example.com",
								),
						),
				(
						"我買@example.com",
						ValidatedEmail(
								local_part="我買",
								smtputf8=True,
								ascii_domain="example.com",
								domain="example.com",
								email="我買@example.com",
								original_email="我買@example.com",
								),
						),
				(
						"甲斐黒川日本@example.com",
						ValidatedEmail(
								local_part="甲斐黒川日本",
								smtputf8=True,
								ascii_domain="example.com",
								domain="example.com",
								email="甲斐黒川日本@example.com",
								original_email="甲斐黒川日本@example.com",
								),
						),
				param(
						"чебурашкаящик-с-апельсинами.рф@example.com",
						ValidatedEmail(
								local_part="чебурашкаящик-с-апельсинами.рф",
								smtputf8=True,
								ascii_domain="example.com",
								domain="example.com",
								email="чебурашкаящик-с-апельсинами.рф@example.com",
								original_email="чебурашкаящик-с-апельсинами.рф@example.com",
								),
						marks=pytest.mark.skipif(
								sys.platform == "win32" and PYPY36,
								reason="Fails due to unicode issue with filename",
								),
						id="unicode_1",
						),
				(
						"उदाहरण.परीक्ष@domain.with.idn.tld",
						ValidatedEmail(
								local_part="उदाहरण.परीक्ष",
								smtputf8=True,
								ascii_domain="domain.with.idn.tld",
								domain="domain.with.idn.tld",
								email="उदाहरण.परीक्ष@domain.with.idn.tld",
								original_email="उदाहरण.परीक्ष@domain.with.idn.tld",
								),
						),
				(
						"ιωάννης@εεττ.gr",
						ValidatedEmail(
								local_part="ιωάννης",
								smtputf8=True,
								ascii_domain="xn--qxaa9ba.gr",
								domain="εεττ.gr",
								email="ιωάννης@εεττ.gr",
								original_email="ιωάννης@εεττ.gr",
								),
						),
				],
		)
def test_email_valid(
		email_input: str,
		output: ValidatedEmail,
		advanced_file_regression: AdvancedFileRegressionFixture,
		):
	# print(f'({email_input!r}, {validate_email(email_input)!r}),')
	assert validate_email(email_input) == output

	data = output.as_dict()
	data["__repr__"] = repr(output)
	data["__str__"] = str(output)
	advanced_file_regression.check(json.dumps(data), extension=".json")


@pytest.mark.parametrize(
		"email_input,error_msg",
		[
				("my@.leadingdot.com", "An email address cannot have a period immediately after the @-sign."),
				("my@．．leadingfwdot.com", "An email address cannot have a period immediately after the @-sign."),
				("my@..twodots.com", "An email address cannot have a period immediately after the @-sign."),
				("my@twodots..com", "An email address cannot have two periods in a row."),
				(
						"my@baddash.-.com",
						{
								"The domain name baddash.-.com contains invalid characters (Label must not start or end with a hyphen).",
								"The domain name baddash.-.com contains invalid characters (The label b'-' is not a valid A-label).",
								}
						),
				(
						"my@baddash.-a.com",
						{
								"The domain name baddash.-a.com contains invalid characters (Label must not start or end with a hyphen).",
								"The domain name baddash.-a.com contains invalid characters (The label b'-a' is not a valid A-label).",
								}
						),
				(
						"my@baddash.b-.com",
						{
								"The domain name baddash.b-.com contains invalid characters (Label must not start or end with a hyphen).",
								"The domain name baddash.b-.com contains invalid characters (The label b'b-' is not a valid A-label)."
								}
						),
				(
						'my@example.com\n',
						{
								'The domain name example.com\n contains invalid characters (Codepoint U+000A at position 4 of \'com\\n\' not allowed).',
								"The domain name example.com\n contains invalid characters (Codepoint U+000A not allowed at position 12 in 'example.com\\n').",
								}
						),
				(
						'my@example\n.com',
						{
								"The domain name example\n.com contains invalid characters (Codepoint U+000A at position 8 of 'example\\n' not allowed).",
								"The domain name example\n.com contains invalid characters (Codepoint U+000A not allowed at position 8 in 'example\\n.com').",
								}
						),
				(".leadingdot@domain.com", "The email address contains invalid characters before the @-sign: .."),
				("..twodots@domain.com", "The email address contains invalid characters before the @-sign: .."),
				(
						"twodots..here@domain.com",
						"The email address contains invalid characters before the @-sign: .."
						),
				(
						"me@⒈wouldbeinvalid.com",
						"The domain name ⒈wouldbeinvalid.com contains invalid characters (Codepoint U+2488 not allowed "
						"at position 1 in '⒈wouldbeinvalid.com')."
						),
				("@example.com", "There must be something before the @-sign."),
				('\nmy@example.com', 'The email address contains invalid characters before the @-sign: \n.'),
				('m\ny@example.com', 'The email address contains invalid characters before the @-sign: \n.'),
				('my\n@example.com', 'The email address contains invalid characters before the @-sign: \n.'),
				(
						"11111111112222222222333333333344444444445555555555666666666677777@example.com",
						"The email address is too long before the @-sign (1 character too many)."
						),
				(
						"111111111122222222223333333333444444444455555555556666666666777777@example.com",
						"The email address is too long before the @-sign (2 characters too many)."
						),
				(
						"me@1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.111111111122222222223333333333444444444455555555556.com",
						"The email address is too long after the @-sign."
						),
				(
						"my.long.address@1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.11111111112222222222333333333344444.info",
						"The email address is too long (2 characters too many)."
						),
				(
						"my.long.address@λ111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.11111111112222222222333333.info",
						"The email address is too long (when converted to IDNA ASCII)."
						),
				(
						"my.long.address@λ111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.1111111111222222222233333333334444.info",
						"The email address is too long (at least 1 character too many)."
						),
				(
						"my.λong.address@1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.111111111122222222223333333333444.info",
						"The email address is too long (when encoded in bytes)."
						),
				(
						"my.λong.address@1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.1111111111222222222233333333334444444444555555555.6666666666777777777788888888889999999999000000000.1111111111222222222233333333334444.info",
						"The email address is too long (at least 1 character too many)."
						),
				("local_part_only@", "There must be something after the @-sign."),
				("dom@example.com.", "An email address cannot end with a period."),
				],
		)
def test_email_invalid(email_input, error_msg):
	with pytest.raises(EmailSyntaxError) as exc_info:
		validate_email(email_input)
	# print(f'({email_input!r}, {str(exc_info.value)!r}),')

	if isinstance(error_msg, set):
		assert str(exc_info.value) in error_msg
	else:
		assert str(exc_info.value) == error_msg


def test_dict_accessor():
	input_email = "testaddr@example.com"
	valid_email = validate_email(input_email)
	assert isinstance(valid_email.as_dict(), dict)
	assert valid_email.as_dict()["original_email"] == input_email


def test_main_single_good_input(monkeypatch, capsys):
	# stdlib
	import json
	test_email = "test@example.com"
	monkeypatch.setattr("sys.argv", ["email_validator", test_email])
	validator_main()
	stdout, _ = capsys.readouterr()
	output = json.loads(str(stdout))
	assert isinstance(output, dict)
	assert validate_email(test_email).original_email == output["original_email"]


def test_main_single_bad_input(monkeypatch, capsys):
	bad_email = "test@..com"
	monkeypatch.setattr("sys.argv", ["email_validator", bad_email])
	validator_main()
	stdout, _ = capsys.readouterr()
	assert stdout == 'An email address cannot have a period immediately after the @-sign.\n'


def test_main_multi_input(monkeypatch, capsys):
	# stdlib
	import io
	test_cases = ["test@example.com", "test2@example.com", "test@.com", "test3@.com"]
	test_input = io.StringIO('\n'.join(test_cases))
	monkeypatch.setattr("sys.stdin", test_input)
	monkeypatch.setattr("sys.argv", ["email_validator"])
	validator_main()
	stdout, _ = capsys.readouterr()
	assert test_cases[0] not in stdout
	assert test_cases[1] not in stdout
	assert test_cases[2] in stdout
	assert test_cases[3] in stdout
