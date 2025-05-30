from typing import Optional

from amocrm.v2 import (
    Company as _Company,
    Contact as _Contact,
    Lead as _Lead,
    custom_field,
    tokens,
)

from core.settings import settings


__all__ = (
    "setup_amocrm",
    "initial_setup_amocrm",
    "Lead",
    "LEAD_FIELDS",
    "LEAD_FIELDS_MAPPING",
)


LEAD_FIELDS = [
    # "compensation_status",
    # "compensation_amount",
    # "pretension_fee_amount",
    "account_protocol",
    "found_link",
    "status",
    "ie_name",
    "ogrn_number",
    "comment",
    "link_to_protocol",
    "link_to_act_design",
    "link_to_act_image",
    "link_to_layouts_storage",
    "link_to_layers_storage",
]

LEAD_FIELDS_MAPPING = {
    # "512865": "pretension_status",
    # "512915": "compensation_status",
    # "512917": "compensation_amount",
    # "512919": "pretension_fee_amount",
    # "571397": "found_link",
    # "571399": "status",
    # "571401": "ie_name",
    # "571403": "ogrn",
    # "571405": "comment",
    # "571455": "link_to_protocol",
    # '1598429': "link_to_act_design",
    # "1598451": "link_to_act_image",
    # "1598447": "link_to_layers_storage",
    # "1598449": "link_to_layouts_storage",
    # "1506561": "account_protocol",
}


class Contact(_Contact):
    dolzhnost = custom_field.TextCustomField("Должность", field_id=506201, code="POSITION")
    telefon = custom_field.ContactPhoneField("Телефон", field_id=506203, code="PHONE")
    email = custom_field.ContactEmailField("Email", field_id=506205, code="EMAIL")
    adres_narushitelia = custom_field.StreetAddressCustomField("Адрес нарушителя", field_id=1610316)
    inn_kontakta = custom_field.NumericCustomField("ИНН контакта", field_id=1611309)


class Company(_Company):
    telefon = custom_field.ContactPhoneField("Телефон", field_id=506203, code="PHONE")
    email = custom_field.ContactEmailField("Email", field_id=506205, code="EMAIL")
    web = custom_field.UrlCustomField("Web", field_id=506207, code="WEB")
    adres = custom_field.TextAreaCustomField("Адрес", field_id=506209, code="ADDRESS")
    iur_litso = custom_field.BaseCustomField("Юр. лицо", field_id=1611311)
    data_registratsii = custom_field.DateCustomField("Дата регистрации", field_id=1612119)


class Lead(_Lead):
    utm_content = custom_field.BaseCustomField("utm_content", field_id=506211, code="UTM_CONTENT")
    utm_medium = custom_field.BaseCustomField("utm_medium", field_id=506213, code="UTM_MEDIUM")
    utm_campaign = custom_field.BaseCustomField("utm_campaign", field_id=506215, code="UTM_CAMPAIGN")
    utm_source = custom_field.BaseCustomField("utm_source", field_id=506217, code="UTM_SOURCE")
    utm_term = custom_field.BaseCustomField("utm_term", field_id=506219, code="UTM_TERM")
    utm_referrer = custom_field.BaseCustomField("utm_referrer", field_id=506221, code="UTM_REFERRER")
    roistat = custom_field.BaseCustomField("roistat", field_id=506223, code="ROISTAT")
    referrer = custom_field.BaseCustomField("referrer", field_id=506225, code="REFERRER")
    openstat_service = custom_field.BaseCustomField("openstat_service", field_id=506227, code="OPENSTAT_SERVICE")
    openstat_campaign = custom_field.BaseCustomField("openstat_campaign", field_id=506229, code="OPENSTAT_CAMPAIGN")
    openstat_ad = custom_field.BaseCustomField("openstat_ad", field_id=506231, code="OPENSTAT_AD")
    openstat_source = custom_field.BaseCustomField("openstat_source", field_id=506233, code="OPENSTAT_SOURCE")
    from_ = custom_field.BaseCustomField("from", field_id=506235, code="FROM")
    gclientid = custom_field.BaseCustomField("gclientid", field_id=506237, code="GCLIENTID")
    ym_uid = custom_field.BaseCustomField("_ym_uid", field_id=506239, code="_YM_UID")
    ym_counter = custom_field.BaseCustomField("_ym_counter", field_id=506241, code="_YM_COUNTER")
    gclid = custom_field.BaseCustomField("gclid", field_id=506243, code="GCLID")
    yclid = custom_field.BaseCustomField("yclid", field_id=506245, code="YCLID")
    fbclid = custom_field.BaseCustomField("fbclid", field_id=506247, code="FBCLID")
    found_link = custom_field.UrlCustomField("Ссылка на совпадение", field_id=571397)

    class OBEM_VOROVSTVA_ENUMS:
        kartochka_tselikom = custom_field.SelectValue(id=312143, value="карточка целиком")
        tolko_glavnaia = custom_field.SelectValue(id=312145, value="только главная")
        dop_foto_dizain = custom_field.SelectValue(id=312147, value="доп фото дизайн")
        vorovstvo_s_pererabotkoi = custom_field.SelectValue(id=312149, value="воровство с переработкой")
        tolko_foto = custom_field.SelectValue(id=312151, value="только фото")
        ne_nash_maket = custom_field.SelectValue(id=920171, value="не наш макет")
        ne_nash_tovar = custom_field.SelectValue(id=920173, value="не наш товар")
        kartochka_udalena = custom_field.SelectValue(id=920175, value="карточка удалена")
        nash_prodavets = custom_field.SelectValue(id=920177, value="наш продавец")
        prisoedinenie_k_laura = custom_field.SelectValue(id=920179, value="ПРИСОЕДИНЕНИЕ к Laura Rossi")
        prisoedinenie_k_lissom = custom_field.SelectValue(id=920181, value="ПРИСОЕДИНЕНИЕ к Lissom")
        prisoedinenie_k_fngeen = custom_field.SelectValue(id=920183, value="ПРИСОЕДИНЕНИЕ к FNGEEN")
        prisoedinenie_k_riukzaki = custom_field.SelectValue(id=920185, value="ПРИСОЕДИНЕНИЕ к Рюкзаки Simbolic")
        prisoedinenie_k_alevion = custom_field.SelectValue(id=920187, value="ПРИСОЕДИНЕНИЕ к Alevion")
        prisoedinenie_k_alinesl = custom_field.SelectValue(id=920189, value="ПРИСОЕДИНЕНИЕ к Alinesl")
        prisoedinenie_k_alltor = custom_field.SelectValue(id=920191, value="ПРИСОЕДИНЕНИЕ к Alltor")
        prisoedinenie_k_alolis = custom_field.SelectValue(id=920193, value="ПРИСОЕДИНЕНИЕ к Alolis")
        prisoedinenie_k_befosh = custom_field.SelectValue(id=920195, value="ПРИСОЕДИНЕНИЕ к Befosh")
        prisoedinenie_k_beloom = custom_field.SelectValue(id=920197, value="ПРИСОЕДИНЕНИЕ к Beloom")
        prisoedinenie_k_berfi = custom_field.SelectValue(id=920199, value="ПРИСОЕДИНЕНИЕ к Berfi")
        prisoedinenie_k_brary = custom_field.SelectValue(id=920201, value="ПРИСОЕДИНЕНИЕ к Brary")
        prisoedinenie_k_clifo = custom_field.SelectValue(id=920203, value="ПРИСОЕДИНЕНИЕ к Clifo")
        prisoedinenie_k_dantos = custom_field.SelectValue(id=920205, value="ПРИСОЕДИНЕНИЕ к Dantos")
        prisoedinenie_k_ferine = custom_field.SelectValue(id=920207, value="ПРИСОЕДИНЕНИЕ к Ferine")
        prisoedinenie_k_fizzle = custom_field.SelectValue(id=920209, value="ПРИСОЕДИНЕНИЕ к Fizzle")
        prisoedinenie_k_flarix = custom_field.SelectValue(id=920211, value="ПРИСОЕДИНЕНИЕ к Flarix")
        prisoedinenie_k_galaxy = custom_field.SelectValue(id=920213, value="ПРИСОЕДИНЕНИЕ к Galaxy Shop")
        prisoedinenie_k_gellil = custom_field.SelectValue(id=920215, value="ПРИСОЕДИНЕНИЕ к Gellil")
        prisoedinenie_k_glomp = custom_field.SelectValue(id=920217, value="ПРИСОЕДИНЕНИЕ к Glomp")
        prisoedinenie_k_goider = custom_field.SelectValue(id=920219, value="ПРИСОЕДИНЕНИЕ к Goider")
        prisoedinenie_k_happy = custom_field.SelectValue(id=920221, value="ПРИСОЕДИНЕНИЕ к Happy Home")
        prisoedinenie_k_jalent = custom_field.SelectValue(id=920241, value="ПРИСОЕДИНЕНИЕ к Jalent")
        prisoedinenie_k_jasmilar = custom_field.SelectValue(id=920243, value="ПРИСОЕДИНЕНИЕ к Jasmilar")
        prisoedinenie_k_jerta = custom_field.SelectValue(id=920245, value="ПРИСОЕДИНЕНИЕ к Jerta")
        prisoedinenie_k_klonti = custom_field.SelectValue(id=920247, value="ПРИСОЕДИНЕНИЕ к Klonti")
        prisoedinenie_k_lakemun = custom_field.SelectValue(id=920249, value="ПРИСОЕДИНЕНИЕ к Lakemun")
        prisoedinenie_k_leroll = custom_field.SelectValue(id=920251, value="ПРИСОЕДИНЕНИЕ к Leroll")
        prisoedinenie_k_letont = custom_field.SelectValue(id=920253, value="ПРИСОЕДИНЕНИЕ к Letont")
        prisoedinenie_k_levud = custom_field.SelectValue(id=920255, value="ПРИСОЕДИНЕНИЕ к Levud")
        prisoedinenie_k_limtim = custom_field.SelectValue(id=920257, value="ПРИСОЕДИНЕНИЕ к LimTim")
        prisoedinenie_k_limuvil = custom_field.SelectValue(id=920259, value="ПРИСОЕДИНЕНИЕ к Limuvil")
        prisoedinenie_k_lion = custom_field.SelectValue(id=920261, value="ПРИСОЕДИНЕНИЕ к Lion Francesco")
        prisoedinenie_k_lumray = custom_field.SelectValue(id=920263, value="ПРИСОЕДИНЕНИЕ к Lumray")
        prisoedinenie_k_limfan = custom_field.SelectValue(id=920265, value="ПРИСОЕДИНЕНИЕ к Limfan")
        prisoedinenie_k_nimefel = custom_field.SelectValue(id=920267, value="ПРИСОЕДИНЕНИЕ к Nimefel")
        prisoedinenie_k_nobles = custom_field.SelectValue(id=920269, value="ПРИСОЕДИНЕНИЕ к Nobles")
        prisoedinenie_k_noteler = custom_field.SelectValue(id=920271, value="ПРИСОЕДИНЕНИЕ к Noteler")
        prisoedinenie_k_plinket = custom_field.SelectValue(id=920291, value="ПРИСОЕДИНЕНИЕ к Plinket")
        prisoedinenie_k_rawor = custom_field.SelectValue(id=920293, value="ПРИСОЕДИНЕНИЕ к Rawor")
        prisoedinenie_k_rensor = custom_field.SelectValue(id=920295, value="ПРИСОЕДИНЕНИЕ к Rensor")
        prisoedinenie_k_rilvex = custom_field.SelectValue(id=920297, value="ПРИСОЕДИНЕНИЕ к Rilvex")
        prisoedinenie_k_rovada = custom_field.SelectValue(id=920299, value="ПРИСОЕДИНЕНИЕ к Rovada")
        prisoedinenie_k_sale = custom_field.SelectValue(id=920301, value="ПРИСОЕДИНЕНИЕ к Sale Club")
        prisoedinenie_k_sale = custom_field.SelectValue(id=920303, value="ПРИСОЕДИНЕНИЕ к Sale Zone")
        prisoedinenie_k_shopping = custom_field.SelectValue(id=920305, value="ПРИСОЕДИНЕНИЕ к Shopping Zone")
        prisoedinenie_k_sunway = custom_field.SelectValue(id=920307, value="ПРИСОЕДИНЕНИЕ к Sunway")
        prisoedinenie_k_tasarti = custom_field.SelectValue(id=920309, value="ПРИСОЕДИНЕНИЕ к Tasarti")
        prisoedinenie_k_tesmand = custom_field.SelectValue(id=920311, value="ПРИСОЕДИНЕНИЕ к Tesmand")
        prisoedinenie_k_tranzor = custom_field.SelectValue(id=920313, value="ПРИСОЕДИНЕНИЕ к Tranzor")
        prisoedinenie_k_twometaltools = custom_field.SelectValue(id=920315, value="ПРИСОЕДИНЕНИЕ к TwoMetalTools")
        prisoedinenie_k_tylzar = custom_field.SelectValue(id=920317, value="ПРИСОЕДИНЕНИЕ к Tylzar")
        prisoedinenie_k_zaltors = custom_field.SelectValue(id=920319, value="ПРИСОЕДИНЕНИЕ к Zaltors")

    status = custom_field.SelectCustomField("Объем воровства", field_id=571399, enums=OBEM_VOROVSTVA_ENUMS)
    ie_name = custom_field.TextAreaCustomField("ИП нарушителя", field_id=571401)
    ogrn_number = custom_field.TextAreaCustomField("ИНН нарушителя", field_id=571403)
    comment = custom_field.TextAreaCustomField("Комментарий", field_id=571405)
    link_to_protocol = custom_field.UrlCustomField("Протокол", field_id=571455)

    class NASH_IP_ENUMS:
        shmeleva = custom_field.SelectValue(id=921861, value="Шмелева")
        kupreenko = custom_field.SelectValue(id=921863, value="Купреенко")
        kruchinin = custom_field.SelectValue(id=921865, value="Кручинин")
        sidorchuk = custom_field.SelectValue(id=921867, value="Сидорчук")
        tseller = custom_field.SelectValue(id=2388885, value="Целлер")

    account_protocol = custom_field.SelectCustomField("Наш ИП", field_id=1506561, enums=NASH_IP_ENUMS)
    nash_ip_nomer_linii = custom_field.TextCustomField("Наш ИП (номер линии)", field_id=1591643)
    link_to_act_design = custom_field.TextAreaCustomField("Акт на дизайн 1", field_id=1598429)
    link_to_layouts_storage = custom_field.TextAreaCustomField("Макеты", field_id=1598447)
    link_to_layers_storage = custom_field.TextAreaCustomField("Послойники", field_id=1598449)
    link_to_act_image = custom_field.TextAreaCustomField("Акт на фото / Акт на 3D", field_id=1598451)
    vnutrennii_no_narusheniia = custom_field.TextAreaCustomField("Внутренний №  нарушения", field_id=1609852)
    vendor_code_real = custom_field.TextAreaCustomField("NLUM", field_id=1610270)
    starye_sluchai = custom_field.TextAreaCustomField("Старые случаи", field_id=1610274)

    class ORGANIZATSIONNO_PRAVOVAIA_FORMA_NARUSHITELIA_ENUMS:
        ooo = custom_field.SelectValue(id=2444298, value="ООО")
        ip = custom_field.SelectValue(id=2444300, value="ИП")
        fiz_litso = custom_field.SelectValue(id=2444302, value="физ.лицо")

    organizatsionno_pravovaia_forma_narushitelia = custom_field.SelectCustomField(
        "Организационно- правовая форма  нарушителя",
        field_id=1610276,
        enums=ORGANIZATSIONNO_PRAVOVAIA_FORMA_NARUSHITELIA_ENUMS,
    )
    tovar = custom_field.TextAreaCustomField("Товар", field_id=1610280)
    artikul_tovara = custom_field.TextAreaCustomField("Артикул товара", field_id=1610282)
    no_protokola = custom_field.TextAreaCustomField("№ протокола", field_id=1610290)
    data_protokola = custom_field.DateCustomField("Дата протокола", field_id=1610292)
    avtor_one = custom_field.TextAreaCustomField("--Автор  1--", field_id=1610296)
    ssylka_na_dogovor_s_avtorom = custom_field.UrlCustomField("Ссылка на договор с автором", field_id=1610298)
    no_dogovora_s_avtorom_one = custom_field.TextAreaCustomField("№ договора с  автором 1", field_id=1610300)
    data_dogovora_s_avtorom_one = custom_field.DateCustomField("Дата договора с автором 1", field_id=1610302)
    ssylka_na_akt_priema_per_proizvedeniia = custom_field.UrlCustomField(
        "Ссылка на акт  приема–пер произведения", field_id=1610304
    )
    ssylka_i_na_skrinshoty_posloinikov = custom_field.UrlCustomField(
        "Ссылка(и) на  скриншоты послойников", field_id=1610308
    )
    raschet_kompensatsii_iskhodia_iz_onezero_zerozerozero_za_kazhdyi_sposob = custom_field.NumericCustomField(
        "Расчет компенсации исходя из 10 000 за каждый способ", field_id=1610310
    )
    raschet_kompensatsii_iskhodia_iz_twozero_zerozerozero_za_kazhdyi_sposob = custom_field.NumericCustomField(
        "Расчет компенсации исходя из 20 000 за каждый способ", field_id=1610312
    )

    class KUDA_NAPRAVLENA_PRETENZIIA_ENUMS:
        pochta = custom_field.SelectValue(id=2445210, value="Почта")
        whatsapp = custom_field.SelectValue(id=2445212, value="WhatsApp")
        email = custom_field.SelectValue(id=2445214, value="Email")

    kuda_napravlena_pretenziia = custom_field.MultiSelectCustomField(
        "Куда направлена претензия", field_id=1610318, enums=KUDA_NAPRAVLENA_PRETENZIIA_ENUMS
    )
    kommentarii_otdela_dp = custom_field.TextAreaCustomField("Комментарии отдела ДП", field_id=1610320)
    chek_po_pretenzii = custom_field.UrlCustomField("Чек по претензии", field_id=1610322)
    trek_nomer_pretenzii = custom_field.TextAreaCustomField("Трек номер претензии", field_id=1610324)
    kod_dostupa_k_trek_nomeru = custom_field.NumericCustomField("Код доступа к трек номеру", field_id=1610326)
    ssylka_dlia_otslezhivaniia_pretenzii_na_pochta_rossii = custom_field.UrlCustomField(
        "Ссылка для отслеживания претензии на Почта России", field_id=1610328
    )
    data_podachi_pretenzii = custom_field.DateCustomField("Дата подачи претензии", field_id=1610330)
    data_okonchaniia_dosudebnogo_sroka = custom_field.DateCustomField(
        "Дата окончания досудебного срока", field_id=1610332
    )
    summa_po_soglasheniiu_o_du = custom_field.NumericCustomField("Сумма по соглашению о ДУ", field_id=1610334)
    kommentarii_otdela_du = custom_field.TextAreaCustomField("Комментарии отдела ДУ", field_id=1610336)
    sud_rassmatrivaiushchii_delo = custom_field.TextAreaCustomField("Суд, рассматривающий дело", field_id=1610338)
    tsena_iska = custom_field.NumericCustomField("Цена иска", field_id=1610340)
    gosposhlina = custom_field.NumericCustomField("Госпошлина", field_id=1610342)
    trek_nomer_iska = custom_field.NumericCustomField("Трек номер Иска", field_id=1610346)
    kod_k_trek_nomeru_iska = custom_field.NumericCustomField("Код к трек номеру Иска", field_id=1610348)
    ssylka_dlia_otslezhivaniia_iska_na_pochta_rossii = custom_field.UrlCustomField(
        "Ссылка для отслеживания Иска на Почта России", field_id=1610350
    )
    data_podachi_iska_otvetchiku = custom_field.DateCustomField("Дата подачи Иска ответчику", field_id=1610352)
    chek_ob_otpravke_iska_otvetchiku = custom_field.UrlCustomField("Чек об отправке Иска ответчику", field_id=1610354)
    data_otpravki_iska_v_sud = custom_field.DateCustomField("Дата отправки иска в Суд", field_id=1610356)
    nomer_dela_v_sude = custom_field.TextAreaCustomField("Номер дела в Суде", field_id=1610358)
    data_zaneseniia_inf_o_reshenii_suda = custom_field.DateCustomField(
        "Дата занесения инф. о решении суда", field_id=1610360
    )
    komment_iue_po_delu = custom_field.TextAreaCustomField("Коммент ЮЭ по делу", field_id=1610362)
    vyigrannaia_summa_bez_poshliny = custom_field.NumericCustomField("Выигранная сумма (без пошлины)", field_id=1610364)
    razmer_kompensatsii_sud_raskhodov = custom_field.NumericCustomField(
        "Размер компенсации суд. расходов", field_id=1610366
    )
    data_zaprosa_ispol_lista = custom_field.DateCustomField("Дата запроса испол.листа", field_id=1610368)
    nomer_ispol_proizvodstva = custom_field.TextAreaCustomField("Номер испол. производства", field_id=1610372)
    komment_iue_po_ispol_proizvodstvu = custom_field.TextAreaCustomField(
        "Коммент ЮЭ по Испол. производству", field_id=1610374
    )
    avtor_two = custom_field.TextAreaCustomField("--Автор 2--", field_id=1611247)
    avtor_three = custom_field.TextAreaCustomField("--Автор 3--", field_id=1611249)

    class MARKETPLEIS_ENUMS:
        wb = custom_field.SelectValue(id=2664523, value="WB")
        ozon = custom_field.SelectValue(id=2664525, value="Ozon")
        yandex_market = custom_field.SelectValue(id=2664527, value="Yandex market")
        kazan_express = custom_field.SelectValue(id=2664529, value="Kazan express")
        mega_market = custom_field.SelectValue(id=2664531, value="Mega market")
        aliexpress = custom_field.SelectValue(id=2664533, value="Aliexpress")
        inoe = custom_field.SelectValue(id=2664535, value="Иное")

    marketpleis = custom_field.SelectCustomField("Маркетплейс", field_id=1611291, enums=MARKETPLEIS_ENUMS)
    skolko_ukradeno_foto_three_sposoba = custom_field.NumericCustomField(
        "Сколько украдено фото 3 способа", field_id=1611295
    )
    skolko_ukradeno_foto_four_sposoba = custom_field.NumericCustomField(
        "Сколько украдено фото 4 способа", field_id=1611297
    )
    skolko_ukradeno_dizainov_three_sposoba = custom_field.NumericCustomField(
        "Сколько украдено дизайнов 3 способа", field_id=1611299
    )
    skolko_ukradeno_dizainov_four_sposoba = custom_field.NumericCustomField(
        "Сколько украдено дизайнов 4 способа", field_id=1611301
    )
    obshchee_kol_vo_narushenii = custom_field.NumericCustomField("Общее кол-во нарушений", field_id=1611303)

    class UDALEN_LI_KONTENT_ENUMS:
        da = custom_field.SelectValue(id=2664545, value="Да")
        net = custom_field.SelectValue(id=2664547, value="Нет")

    udalen_li_kontent = custom_field.SelectCustomField(
        "Удален ли контент", field_id=1611305, enums=UDALEN_LI_KONTENT_ENUMS
    )

    class STATUS_SAMOZANIATOGO_ENUMS:
        da = custom_field.SelectValue(id=2665037, value="Да")
        net = custom_field.SelectValue(id=2665039, value="Нет")

    status_samozaniatogo = custom_field.SelectCustomField(
        "Статус самозанятого", field_id=1611307, enums=STATUS_SAMOZANIATOGO_ENUMS
    )
    nomer_ispol_lista = custom_field.TextAreaCustomField("Номер испол. листа", field_id=1611315)
    data_ispol_lista = custom_field.DateCustomField("Дата испол. листа", field_id=1611317)
    raschet_kompensatsii_iskhodia_iz_onefive_zerozerozero_za_kazhdyi_sposob = custom_field.NumericCustomField(
        "Расчет компенсации исходя из 15 000 за каждый способ", field_id=1611319
    )
    fio = custom_field.TextAreaCustomField("ФИО", field_id=1611427)

    class PORIADOK_RASSMOTRENIIA_ENUMS:
        obshchii = custom_field.SelectValue(id=2835881, value="Общий")
        uproshchennyi = custom_field.SelectValue(id=2835883, value="Упрощенный")

    poriadok_rassmotreniia = custom_field.SelectCustomField(
        "Порядок рассмотрения", field_id=1611677, enums=PORIADOK_RASSMOTRENIIA_ENUMS
    )

    class KUDA_SPERVA_OTPRAVLIAT_LIST_ENUMS:
        bank = custom_field.SelectValue(id=2860595, value="Банк")
        fssp = custom_field.SelectValue(id=2860597, value="ФССП")

    kuda_sperva_otpravliat_list = custom_field.SelectCustomField(
        "Куда сперва отправлять лист", field_id=1611789, enums=KUDA_SPERVA_OTPRAVLIAT_LIST_ENUMS
    )
    ssylka_na_dogovor_s_avtorom_two = custom_field.UrlCustomField("Ссылка на договор с автором 2", field_id=1611921)
    no_dogovora_s_avtorom_two = custom_field.TextCustomField("№ договора с  автором 2", field_id=1611923)
    no_dogovora_s_avtorom_three = custom_field.TextCustomField("№ договора с  автором 3", field_id=1611925)
    data_dogovora_s_avtorom_two = custom_field.DateCustomField("Дата договора с  автором 2", field_id=1611927)
    data_dogovora_s_avtorom_three = custom_field.DateCustomField("Дата договора с автором 3", field_id=1611929)
    ssylka_na_dogovor_s_avtorom_three = custom_field.UrlCustomField("Ссылка на договор с автором 3", field_id=1611931)
    fio_two = custom_field.TextCustomField("ФИО 2", field_id=1611933)
    fio_three = custom_field.TextCustomField("ФИО 3", field_id=1611935)
    akt_na_dizain_two = custom_field.TextAreaCustomField("Акт на дизайн 2", field_id=1611937)
    akt_na_dizain_three = custom_field.TextAreaCustomField("Акт на дизайн 3", field_id=1611939)
    data_akta_p_p_ot_avtora_one = custom_field.DateCustomField("Дата акта п/п от автора 1", field_id=1612107)
    data_akta_p_p_ot_avtora_two = custom_field.DateCustomField("Дата акта п/п от автора 2", field_id=1612109)
    data_akta_p_p_ot_avtora_three = custom_field.DateCustomField("Дата акта п/п от автора 3", field_id=1612111)
    vsego_ukradeno_foto = custom_field.NumericCustomField("Всего украдено Фото", field_id=1612113)
    vsego_ukradeno_dizainov = custom_field.NumericCustomField("Всего украдено Дизайнов", field_id=1612115)
    nalichie_pererabotki = custom_field.TextAreaCustomField("Наличие переработки", field_id=1612117)
    otvetstvennyi_ot_odp = custom_field.TextCustomField("Ответственный от ОДП", field_id=1612589)
    otdel_iue = custom_field.TextCustomField("Отдел ЮЭ", field_id=1612591)
    otdel_dosudeb_uregulirovaniia = custom_field.TextCustomField("Отдел Досудеб.урегулирования", field_id=1612593)
    data_sudebnogo_zasedaniia = custom_field.DateCustomField("Дата судебного заседания", field_id=1612597)
    razmer_chastichnoi_oplaty = custom_field.NumericCustomField("Размер частичной оплаты", field_id=1612599)
    nomer_dogovora_na_sud_raskhody = custom_field.TextCustomField("Номер договора на суд. расходы", field_id=1612661)
    data_dogovora_s_ip_iuristom = custom_field.DateCustomField("Дата договора  с ИП-юристом", field_id=1612663)
    summa_dogovora_s_ip_iuristom = custom_field.NumericCustomField("Сумма договора с ИП-юристом", field_id=1612665)

    def _get_updated_data(self) -> dict:
        """Fix bug in AMOCRM library when unexpected field is_computed is present in custom_fields_values"""
        data = super()._get_updated_data()
        for item in data.get("custom_fields_values", []):
            if "is_computed" in item:
                del item["is_computed"]

        return data


class InMemoryTokensStorage(tokens.TokensStorage):
    def __init__(self, access_token: str, refresh_token: str):
        self._access_token = access_token
        self._refresh_token = refresh_token
        self.should_be_refreshed = False

    def get_access_token(self) -> Optional[str]:
        return self._access_token

    def get_refresh_token(self) -> Optional[str]:
        return self._refresh_token

    def save_tokens(self, access_token: str, refresh_token: str):
        self._access_token, self._refresh_token = access_token, refresh_token
        self.should_be_refreshed = True

    def mark_refreshed(self):
        self.should_be_refreshed = False


def setup_amocrm(
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> InMemoryTokensStorage:
    in_memory_tokens_storage = InMemoryTokensStorage(
        access_token=access_token,
        refresh_token=refresh_token,
    )
    tokens.default_token_manager(
        client_id=settings.AMOCRM_CLIENT_ID,
        client_secret=settings.AMOCRM_CLIENT_SECRET,
        subdomain=settings.AMOCRM_SUBDOMAIN,
        redirect_url=f"{settings.URL}/api/v1/stolen_content/webhook",
        storage=in_memory_tokens_storage,
    )
    return in_memory_tokens_storage


def initial_setup_amocrm(auth_code: str):
    tokens.default_token_manager.init(code=auth_code, skip_error=True)
