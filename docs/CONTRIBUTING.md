# Contributing

Thank you for wanting to help. You do not need to be a programmer for most of this.

## The easiest ways to help (no code)

1. **Report a mistake.** Open a speaker's sheet and tap **Report an error**, or [open an issue](https://github.com/omshivaprakash/litfest-speaker-guide/issues/new). Tell us:
   - *Who* (the person's name)
   - *Which festival*
   - *What is wrong, and what is right* (with a link to the source if you have one)
2. **Suggest a festival.** Open an issue with the festival's name and website. The best suggestions point to a page or feed that lists speakers.
3. **Tell us a speaker list has changed.** The daily check catches most changes, but a note from someone who knows the festival helps.
4. **Check the Kannada and Hindi labels.** They are a first version. Tell us what reads awkwardly and what it should say.
5. **If you represent a festival, author or photographer:** tell us if anything should be corrected, updated or removed. We will act on it.

## If you are a developer

- Read [How it works](HOW-IT-WORKS.md), then [Maintaining](MAINTAINING.md).
- Fork the repo, make a change, and open a pull request.
- Before you do, run:
  ```
  python3 tools/validate.py
  python3 -m http.server 8765 &
  node tests/run.js
  ```
- Keep these house rules:
  - **No screen may scroll the page.** Each tab fits one screen and pages through content.
  - **No outside requests at load.** Keep images, fonts and data inside the repo.
  - **Say when something is a guess.** Never present an inferred field as fact.
  - **Do not hide data.** If a festival has no bio or photo for someone, show the person anyway and say so.
  - **Stay plain.** No framework, no build step.
- Run `python3 tools/stamp.py` after changing `index.html`, `explore.js`, `i18n.js` or data, so installed copies refresh.

## Respecting the people listed

Names, photos and bios here come from public festival pages and belong to their owners. Please keep it that way: only add information a festival has itself published, and credit the source.

## Code of conduct

Be kind. Assume good faith. This is a small, free project built out of love for books.

## License

By contributing you agree your contribution is released under the MIT license (see [LICENSE](../LICENSE)).
