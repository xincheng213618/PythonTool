import requests
import javdb
new_url ="https://javdb.com/v/DZmy3"

javlibrary_cookie = "list_mode=h; theme=auto; locale=zh; over18=1; comment_warning=1; _ym_uid=1743432317221724263; _ym_d=1743432317; hide_app_banner=1; cf_clearance=GdJs3UnOyzaEAp9C40Ia7ZhGvpE7R5KJEkvho9F.EA8-1751215328-1.2.1.1-kMZvTGWx0NylMBqYazZK2m1kD.2DJKt9gW0Migkkjdav_ui7O8pyQgrn0xfqkpYy4eifbVLz.drdExFd4Jioon70FZ.trEuw2etnGOD3dPHSgH8_QbI.SOz.2eThBfoK2IUDN1ecgWLcmVVKmgU2ZqakIE6LgH1vw9ddvBgotaJPU3Zl6Rjdq.CFUq6FQo4TyJdQHupwPP7O9cpr_HLjl4wsIbJfWQMqvPIhMfjCOwaCpxEzrtxXe_oqSfz5VaUI83mfOwtsfLWiwr_m3SRTBskfAqmLvN0cP9tFe7Sa3TBYesJy0wyCGu6PDyceND52a0CAIVhh0GmDsghcMeHzgIB1y9mHs4ZriL5lvy_zfEc; _jdb_session=XLWsqlHMifGS5q%2BoNS8IjqEUqKguVLexQCqyylpgAE1hobmQyGgDSi3ZqDMTvcbo%2BOU5JWohryOV2gHFI5LzOHx3dFIwmsE3aMbBiEH6msVRen2G6o%2BYE%2BOF9pCTojS24u3Mc%2FoM8eVrUsr41PFVuao772JKiBKRNHMexJPIG%2BXS%2Fd89OBeorw5yJ%2BZmgfspHkFc17Ney3EkeLOLwoP4oW7%2FLnu3nBNXv5vzr4dsy9eYMj7Zl%2B3kKx056O2XkU42uP7Pxfd65kmJtduvhcqKaXSHgve05AEmg%2F8MuXhsRh8p%2F%2FuOJazypm8ujYEWZqabq%2BiDn8ncXL850x6L5C51FLjga1g30GnXJApTnDQL0ehMg5IMYOlXvIgzNfQx1U5gTok%3D--TTGteI1Q1u1zgl%2FH--IfJ%2Fid791WHvdK5s5itUFg%3D%3D"
proxies = {
    "https": "http://127.0.0.1:10809"
}

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    "cookie": javlibrary_cookie
}

# r = requests.get(new_url, headers=headers, proxies=proxies)

# print(r.text)

videoinfo = javdb.getletterinfo("2519228")
print(videoinfo)