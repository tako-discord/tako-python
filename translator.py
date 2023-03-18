import i18n
from discord import Locale
from typing import Optional
from discord import app_commands
from discord.app_commands import TranslationContextLocation

locales = {
    Locale.american_english: "en",
    Locale.british_english: "en",
    Locale.brazil_portuguese: "pt",
    Locale.chinese: "zh",
    Locale.croatian: "hr",
    Locale.dutch: "nl",
    Locale.french: "fr",
    Locale.german: "de",
    Locale.japanese: "ja",
    Locale.polish: "pl",
    Locale.spain_spanish: "es",
    Locale.swedish: "sv",
}


class TakoTranslator(app_commands.Translator):
    async def load(self):
        i18n.set("filename_format", "{locale}.{format}")
        i18n.set("fallback", "en")
        i18n.load_path.append("i18n")

    async def translate(
        self,
        string: app_commands.locale_str,
        locale: Locale,
        context: app_commands.TranslationContextTypes,
    ) -> Optional[str]:
        try:
            locale_str = locales[locale]
        except KeyError:
            return None
        other = False
        if context.location == TranslationContextLocation.other:
            other = True
        try:
            translation = i18n.t(
                f"{'' if other else str(context.location).replace('TranslationContextLocation.', '')}.{string.message}",
                locale=locale_str,
                **string.extras,
            )
        except:
            translation = f"{str(context.location).replace('TranslationContextLocation.', '')}.{string.message}"
        return (
            translation
            if not translation
            == f"{'' if other else str(context.location).replace('TranslationContextLocation.', '')}.{string.message}"
            else None
        )
