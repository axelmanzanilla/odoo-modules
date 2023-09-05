/** @odoo-module */

import { patch } from 'web.utils';
import { NavBar } from "@web/webclient/navbar/navbar";
import { computeAppsAndMenuItems } from "@web/webclient/menus/menu_helpers";

patch(NavBar.prototype, 'backend_main_menu_website/static/src/webclient/navbar/navbar.js', {
    setup() {
        this._super();
        let { apps } = computeAppsAndMenuItems(this.menuService.getMenuAsTree("root"));
        this._menu_app = apps.find(app => app.xmlid = "backend_main_menu_website.backend_main_menu_website_root");
    },
    onClickMenu(){
        this.onNavBarDropdownItemSelection(this._menu_app);
    }
});
