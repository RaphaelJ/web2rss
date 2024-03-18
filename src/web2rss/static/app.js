/*
 * Copyright (C) 2024 Raphael Javaux
 * raphael@noisycamp.com
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 3 of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
 */


const app = Vue.createApp({})

let FeedIframe = {
    props: {
        url: { type: String, required: true },

        article_selector: { type: String, required: true },
        url_selector: { type: String, required: true },
        title_selector: { type: String, required: true },
        date_selector: { type: String, required: true },
        summary_selector: { type: String, required: true },

        active_selector: { type: String, required: false },
    },
    data() {
        return {
        }
    },
    mounted() {

    },
    template: `
        <div
            style="
                width: 100%;
                height: 600px;
                border: var(--bs-border-width) solid var(--bs-border-color);
                border-radius: var(--bs-border-radius);
                position: relative;">

            <div
                v-if="!active_selector"
                style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    height: 100%;
                    width: 100%;
                    border-radius: var(--bs-border-radius);

                    z-index: 1;

                    background-color: rgba(0, 0, 0, 0.4);
                    backdrop-filter: blur(6px);

                    color: white;
                    text-shadow: 0 0 1px black;
                    text-align: center;">

                <p
                    class="display-6"
                    style="
                        --line-height: 50px;

                        position: absolute;
                        top: calc(50% - var(--line-height) / 2);
                        left: 0;

                        line-height: --line-height;

                        width: 100%;

                        text-align: center">
                    Select a content selector first <i class="bi bi-hand-index"></i>
                </p>
            </div>

            <iframe
                ref="iframe"
                :src="url"
                style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    height: 100%;
                    width: 100%;

                    border-radius: var(--bs-border-radius);

                    z-index: 0;">
            </iframe>
        </div>
    `,
    computed: {
        highlighted_elements()
        {
            let iframe = this.$refs["iframe"]

            iframe
        }
    },
    methods: {
    }
}

app.component("feed-iframe", FeedIframe)

app.mount('#app')

