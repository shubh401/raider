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

async function unzip_crx(extension_path, target_dir) {
    const {default: unzip} = await import("unzip-crx-3");
    try {
        unzip(extension_path, target_dir).then(() => {
            console.log("Done!");
        });
    } catch (e) {
        console.error(e);
    } finally {
        return;
    }
}

if (process.argv.length == 4) {
    let extension_path = process.argv[2];
    let target_dir = process.argv[3];
    unzip_crx(extension_path, target_dir);
} else {
    console.log("Invalid arguments! Please provide appropriate arguments.")
}