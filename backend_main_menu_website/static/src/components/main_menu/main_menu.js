/** @odoo-module **/

import { Component } from  "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

class MenuAction extends Component {
    setup() {
        this.menuService = useService("menu");
        this.apps = this.menuService.getApps()
                        .filter(app => app.xmlid != "backend_main_menu_website.backend_main_menu_website_root")
                        .sort((a, b) => (a.name > b.name) ? 1 : ((b.name > a.name) ? -1 : 0));
    }

    onClickModule(menu){
        if(menu) this.menuService.selectMenu(menu);
    }
}

MenuAction.template = "backend_main_menu_website.MainMenu";

registry
    .category("actions")
    .add("backend_main_menu_website.action_open_main_menu", MenuAction);
