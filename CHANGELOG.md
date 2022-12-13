# Changelog

<a name="0.3.0"></a>
## 0.3.0 (2022-12-13)

### Added

- ✨ add clear all (&#x60;/clear amount:0&#x60;) [[9421d10](https://github.com/tako-discord/tako/commit/9421d10f15b44d7743519cd59d176289b51f0f32)]

### Changed

- 🔧 don&#x27;t hide entries from &#x60;.gitignore&#x60; in vsls [[9ea50a4](https://github.com/tako-discord/tako/commit/9ea50a48044970d0c39ba71ba1e5c89c381f0643)]
- 🚸 automatically remove attachments that are too large [[c04876f](https://github.com/tako-discord/tako/commit/c04876ff33ef047746f591e8a38f63bcbf960fc2)]
- 🍱 update bars [[9fd2488](https://github.com/tako-discord/tako/commit/9fd24884a15fa0ab1dff92fe229eca5f1bf89fe3)]
- 💄 beautify da README.md [[0cedaa0](https://github.com/tako-discord/tako/commit/0cedaa0fdb58d2ba26e4794442b34254f9f78746)]
- 👽 switch translation api to tl.tako-bot.com [[3505691](https://github.com/tako-discord/tako/commit/35056915ab977ffd14905059214756600eca1a14)]

### Fixed

- 🚑 add support for &#x60;active_dev&#x60; flag [[c94bc23](https://github.com/tako-discord/tako/commit/c94bc235bfb49d1f69fb81d3ada7b05a9fe76e4b)]

### Miscellaneous

- ⚰️ removed unused imports in &#x60;autotranslate.py&#x60; [[acb3352](https://github.com/tako-discord/tako/commit/acb335289f4633a80a96feb88e9b295ae8d08366)]
- 🌐 new hebrew translations ([#9](https://github.com/tako-discord/tako/issues/9)) [[b706eb6](https://github.com/tako-discord/tako/commit/b706eb66d73d2c0b857d7b2af77ea08318856bf2)]


<a name="0.2.0"></a>
## 0.2.0 (2022-12-08)

### Added

- ✨ add &#x60;/poll&#x60; [[ccea7e0](https://github.com/tako-discord/tako/commit/ccea7e07e31a76712c3916d28458e570e19fd483)]

### Changed

- ⚡ only use one webhook in autotranslate instead of one for each message [[8453859](https://github.com/tako-discord/tako/commit/8453859322da37f475d09d6349a837c29c79b393)]
- 👽 switch to https://translate.argosopentech.com/ [[f40e954](https://github.com/tako-discord/tako/commit/f40e9549c19b1aacb4b9e33310b75e79223043ba)]
- 🔧 switch imgen to &#x60;imgen.tako-bot.com&#x60; [[a6dd0fd](https://github.com/tako-discord/tako/commit/a6dd0fdedc5a3436ba8c50b156f3782249e36bd4)]
- 🚚 move persistent views to &#x60;persistent_views&#x60; dir [[54c0265](https://github.com/tako-discord/tako/commit/54c0265410f3e7f3d5a960aec9481c5424d53d7c)]

### Fixed

- 🚑 forgot something [[6ffb59a](https://github.com/tako-discord/tako/commit/6ffb59a000d879e5b8618dd93accbf3cde996e93)]
- 🐛 only use webhook for the minimal autotranslate [[d474d22](https://github.com/tako-discord/tako/commit/d474d22fa27c55b355909c45cb7619c55c098002)]

### Miscellaneous

-  👷 remove lint workflow on PRs [[722b0b8](https://github.com/tako-discord/tako/commit/722b0b887be1231f5d03d456a69e7f6f6fd114c9)]


<a name="0.1.7"></a>
## 0.1.7 (2022-12-03)

### Changed

- ⚡ only use one webhook in autotranslate instead of one for each message [[15c5e0b](https://github.com/tako-discord/tako/commit/15c5e0bd67efff465c67fbbb3c63266d2dcb0e96)]
- 👽 switch to https://translate.argosopentech.com/ [[12dd6f4](https://github.com/tako-discord/tako/commit/12dd6f49f23c8f5a8540bd602c1cfa00e3a65aea)]

### Fixed

- 🐛 fix autotranslate translating it's own translations [[15c5e0b](https://github.com/tako-discord/tako/commit/15c5e0bd67efff465c67fbbb3c63266d2dcb0e96)]

### Miscellaneous

- 🌐 add auto_translate_delete_original [[c8eeab3](https://github.com/tako-discord/tako/commit/c8eeab30d15e4b922b0d19b85e80d40a205d155a)]


<a name="0.1.6"></a>
## 0.1.6 (2022-12-03)

### Changed

- 🚸 move autotranslate to subcommands and add min_webhook style [[3deae29](https://github.com/tako-discord/tako/commit/3deae29611534bd75462fd9229d1a2822e18fa4a)]
- 🔧 move &#x60;TEST_GUILD&#x60; to secrets [[e9ebfdd](https://github.com/tako-discord/tako/commit/e9ebfdd17aac991b72cfe8967e221d3f4eea9c8d)]


<a name="0.1.5"></a>
## 0.1.5 (2022-12-02)

### Changed

- 👽 update crowdin link in activity [[fdfbbaf](https://github.com/tako-discord/tako/commit/fdfbbaf2ebd545941e8b3c85a0fe870568923c69)]

### Removed

- 🔥 remove crowding gh-action [[e34f20b](https://github.com/tako-discord/tako/commit/e34f20b9ff1714f92db5f3a6f2365a5307f6f14c)]

### Miscellaneous

- 🩹 fixed the webhook syle [[48eb52c](https://github.com/tako-discord/tako/commit/48eb52c92eb4b1b99fa0b8a189a26427f210658d)]


<a name="0.1.4"></a>
## 0.1.4 (2022-12-02)

### Added

- ✨ added autotranslate styles [[c490624](https://github.com/tako-discord/tako/commit/c490624334671808903e75b4529c22c52f7d9bb2)]


<a name="0.1.3"></a>
## 0.1.3 (2022-12-02)

### Fixed

- 🐛 fix owner check not working due to missing params [[a846938](https://github.com/tako-discord/tako/commit/a8469381ce0971ce73458eb4bcc8e15e96fe2898)]

### Miscellaneous

-  👷 add crowding gh-action [[b637e51](https://github.com/tako-discord/tako/commit/b637e51c3d41a24c24b8a9558cf0388c499ad086)]


<a name="0.1.3"></a>
## 0.1.3 (2022-12-02)

### Fixed

- 🐛 fix owner check not working due to missing params [[a846938](https://github.com/tako-discord/tako/commit/a8469381ce0971ce73458eb4bcc8e15e96fe2898)]

### Miscellaneous

-  👷 add crowding gh-action [[b637e51](https://github.com/tako-discord/tako/commit/b637e51c3d41a24c24b8a9558cf0388c499ad086)]
-  Merge branch &#x27;dev&#x27; of https://github.com/tako-discord/tako into dev [[34e2a45](https://github.com/tako-discord/tako/commit/34e2a458f1f90f7791677eac6359a0d0f19a10c2)]


<a name="0.1.2"></a>
## 0.1.2 (2022-12-02)

### Added

- ✨ add latest version notice to stats [[812ddd6](https://github.com/tako-discord/tako/commit/812ddd6db4f7aa85e741aa84ad24894e02a9c369)]

### Changed

- 🔧 add libre translate and switch simplytranslate service [[0560830](https://github.com/tako-discord/tako/commit/056083057bbc7a3b5b88ba2b9a02b28182c25bfd)]
- 🔧 remove TEST_GUILD from config [[8a73043](https://github.com/tako-discord/tako/commit/8a730431ec64670e7a5f965ed7aeb94cdc74ae88)]

### Removed

- ➖ removed BeautifulSoup4 from dependencies [[c94ac4a](https://github.com/tako-discord/tako/commit/c94ac4a527f18a82923d8955e487b9d44f81e819)]

### Fixed

- 🐛 fix mentions in autotranslate and add support for multiline messages [[e858545](https://github.com/tako-discord/tako/commit/e858545d86f5c23eb930189f4c408888f14f7287)]
- 🚑 fixed the autotranslate bug [[6465a6c](https://github.com/tako-discord/tako/commit/6465a6cac8c3d885d278b42af60f8d551aac8a5a)]
- ✏️ fixed a typo in helper.py [[a8afe83](https://github.com/tako-discord/tako/commit/a8afe834439c3fb2e6b764fd444cb08c4abefa57)]


<a name="0.1.1"></a>
## 0.1.1 (2022-12-01)

### Added

- ✨ add adjustable confidence threshold for autotranslate [[968a62a](https://github.com/tako-discord/tako/commit/968a62ab912301ea23769d15b01ef227f1ec6ee0)]


### Miscellaneous

- 🌐 translation support for autotranslate [[4577c73](https://github.com/tako-discord/tako/commit/4577c73893270030de29e51dcfa11c4bed66cbdd)]
- 👥 add all remaining testers and new core dev [[5c1e5b8](https://github.com/tako-discord/tako/commit/5c1e5b8064bf01235e8a819ec52c9d020b1ef146)]


<a name="0.1.0-beta"></a>
## 0.1.0-beta (2022-12-01)

### Added

- 🎉 Initial Commit (Public Beta) [[5b6cf55](https://github.com/tako-discord/tako/commit/5b6cf5562f42daa636966d25a1d87c4a9d4fc47a)]

