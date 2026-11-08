/** @odoo-module **/
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/** Client Action: 3 chỉ số, dữ liệu lấy qua service `orm`. Bấm vào thẻ để mở danh sách tương ứng. */
export class InternDashboard extends Component {
    static template = "intern_owl_widgets.Dashboard";
    static props = { "*": true };

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({ loading: true, salesToday: 0, ordersToday: 0, poToApprove: 0, pickingsPending: 0 });
        onWillStart(() => this.loadData());
    }

    get todayDomain() {
        const start = new Date();
        start.setHours(0, 0, 0, 0);
        const utc = start.toISOString().replace("T", " ").slice(0, 19);
        return [["state", "=", "sale"], ["date_order", ">=", utc]];
    }

    get pickingDomain() {
        return [["state", "in", ["confirmed", "waiting", "assigned"]]];
    }

    async loadData() {
        const [orders, poToApprove, pickingsPending] = await Promise.all([
            this.orm.searchRead("sale.order", this.todayDomain, ["amount_total"]),
            this.orm.searchCount("purchase.order", [["state", "=", "to approve"]]),
            this.orm.searchCount("stock.picking", this.pickingDomain),
        ]);
        this.state.ordersToday = orders.length;
        this.state.salesToday = orders.reduce((sum, order) => sum + order.amount_total, 0);
        this.state.poToApprove = poToApprove;
        this.state.pickingsPending = pickingsPending;
        this.state.loading = false;
    }

    formatMoney(value) {
        return Math.round(value).toLocaleString();
    }

    openList(name, resModel, domain) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name,
            res_model: resModel,
            views: [[false, "list"], [false, "form"]],
            domain,
        });
    }

    openSales() { this.openList("Sales today", "sale.order", this.todayDomain); }
    openPurchases() { this.openList("POs to approve", "purchase.order", [["state", "=", "to approve"]]); }
    openPickings() { this.openList("Pending transfers", "stock.picking", this.pickingDomain); }
}

registry.category("actions").add("intern_owl_widgets.dashboard", InternDashboard);
