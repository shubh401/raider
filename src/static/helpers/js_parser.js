/*
    Copyright (C) 2024 Shubham Agarwal, CISPA.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.
    
    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/


const fs = require("fs");
const escodegen = require("escodegen");
const acorn = require("acorn-loose");

function parse_js(file_path, parent_node = null) {
    return acorn.parse(fs.readFileSync(file_path), {
        allowImportExportEverywhere: true,
        allowAwaitOutsideFunction: true,
        allowReturnOutsideFunction: true,
        allowHashBang: true,
        allowReserved: true,
        locations: true,
        range: true,
        program: parent_node,
    });
}

function init(path) {
    try {
        let parsed_ast = parse_js(path);
        if (parsed_ast) {
            let script_data = escodegen.generate(parsed_ast);
            console.log(script_data);
        }
    } catch(e) {
        console.error(e);
    }
}

if (process.argv.length > 2) {
    init(process.argv[2]);
} else {
    init();
}