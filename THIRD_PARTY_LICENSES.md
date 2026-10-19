# Third-Party Licenses

MLschema depends on the following open-source libraries. We are grateful to their maintainers and contributors.

---

## Runtime Dependencies

### pandas (BSD 3-Clause License)

**Version:** >=3.0.3
**License:** BSD 3-Clause
**Project URL:** <https://pandas.pydata.org/>
**License URL:** <https://github.com/pandas-dev/pandas/blob/main/LICENSE>

```plain
BSD 3-Clause License

Copyright (c) 2008-2011, AQR Capital Management, LLC, Lambda Foundry, Inc. and PyData Development Team
All rights reserved.

Copyright (c) 2011-2025, Open source contributors.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
```

---

### Pydantic (MIT License)

**Version:** >=2.13.4
**License:** MIT
**Project URL:** <https://pydantic.dev/>
**License URL:** <https://github.com/pydantic/pydantic/blob/main/LICENSE>

```
The MIT License (MIT)

Copyright (c) 2017 to present Pydantic Services Inc. and individual contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Development Dependencies

### pytest (MIT License)

**Version:** >=9.0.3
**License:** MIT
**Project URL:** <https://pytest.org/>
**License URL:** <https://github.com/pytest-dev/pytest/blob/main/LICENSE>

Copyright (c) 2004 Holger Krekel and contributors

---

### pytest-cov (MIT License)

**Version:** >=7.1.0
**License:** MIT
**Project URL:** <https://pytest-cov.readthedocs.io/>
**License URL:** <https://github.com/pytest-dev/pytest-cov/blob/master/LICENSE>

Copyright (c) pytest-cov contributors

---

### pytest-mock (MIT License)

**Version:** >=3.15.1
**License:** MIT
**Project URL:** <https://github.com/pytest-dev/pytest-mock/>
**License URL:** <https://github.com/pytest-dev/pytest-mock/blob/main/LICENSE>

Copyright (c) Bruno Oliveira

---

### Ruff (MIT License)

**Version:** >=0.15.15
**License:** MIT
**Project URL:** <https://docs.astral.sh/ruff/>
**License URL:** <https://github.com/astral-sh/ruff/blob/main/LICENSE>

Copyright (c) 2022 Charlie Marsh

---

### Pyright (MIT License)

**Version:** >=1.1.409
**License:** MIT
**Project URL:** <https://github.com/microsoft/pyright>
**License URL:** <https://github.com/microsoft/pyright/blob/main/LICENSE.txt>

Copyright (c) Microsoft Corporation. All rights reserved.

---

### pre-commit (MIT License)

**Version:** >=4.6.0
**License:** MIT
**Project URL:** <https://pre-commit.com/>
**License URL:** <https://github.com/pre-commit/pre-commit/blob/main/LICENSE>

Copyright (c) 2014 pre-commit dev team

---

## Website Dependencies

Astro and Starlight (MIT) build the landing and documentation. The landing's live
form loads MLform (MIT) with its dependencies Lit (BSD-3-Clause) and Zod (MIT);
their license texts are served with the site under `/licenses/`. The playground uses
Vite (MIT), CodeMirror (MIT) and Pyodide (MPL-2.0); its bundled Python runtime and
packages retain their upstream notices. Website dependencies are separate from
the Python package runtime. Exact versions are recorded in `pnpm-lock.yaml`.

Mona Sans and JetBrains Mono use the SIL Open Font License 1.1. Font licenses are
included with the corresponding website assets; the outlined README wordmark's
license is in `brand/mona-sans-LICENSE.txt`.

---

## License Compatibility

The Python runtime depends on pandas (BSD-3-Clause) and Pydantic (MIT). Website tooling and assets retain their own licenses, including Pyodide's MPL-2.0 and the fonts' SIL OFL-1.1.

---

## Attribution

If you use MLschema in your project, please include the following attribution in your documentation or credits:

> This project uses MLschema (<https://github.com/UlloaSP/mlschema>), licensed under the MIT License.
> MLschema depends on pandas and Pydantic, which are also open-source projects.

---

## Reporting Issues

If you believe any license information is incorrect or outdated, please open an issue at:
<https://github.com/UlloaSP/mlschema/issues>

---

**Last Updated:** October 19, 2026
