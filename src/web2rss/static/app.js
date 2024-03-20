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

let FeedSelectorForm = {
    props: {
        action: { type: String, required: true },

        feedUrl: { type: String, required: true },

        article: { type: String, required: false },

        link: { type: String, required: false },
        title: { type: String, required: false },
        date: { type: String, required: false },
        author: { type: String, required: false },
        summary: { type: String, required: false },
    },
    data() {
        const mainSelectorClass = "col-12"
        const subSelectorClass = "col-12 offset-lg-1 col-lg-11"

        return {
            selectors: {
                "article": {
                    class: mainSelectorClass, label: "Article", value: this.article, parent: null,
                },
                "link": {
                    class: subSelectorClass, label: "Link", value: this.link, parent: "article",
                },
                "title": {
                    class: subSelectorClass, label: "Title", value: this.title, parent: "article",
                },
                "date": {
                    class: subSelectorClass, label: "Publication date", value: this.date,
                    parent: "article",
                },
                "author": {
                    class: subSelectorClass, label: "Author", value: this.author,
                    parent: "article",
                },
                "summary": {
                    class: subSelectorClass, label: "Summary", value: this.summary,
                    parent: "article",
                },
            },

            activeSelector: null,
        }
    },
    template: `
        <div class="row row-gap-4">
            <div class="col-12 col-lg-3">
                <form
                    :action="action"
                    method="POST"
                    class="row row-gap-2">
                    <h4>Content selectors</h4>

                    <div class="col-12 form-text">
                        Edit the DOM selectors manually, or visually by clicking on the element.
                    </div>

                    <div
                        v-for="(selector, name) in selectors"
                        :class="selector.class">

                        <label :for="name" class="form-label">
                            <small>{{ selector.label }}</small>
                        </label>

                        <input
                            type="text"
                            class="form-control form-control-sm"
                            :id="name"
                            :name="name"
                            v-model="selector.value"
                            @focusin="select(selector)"
                            @focusout="unselect(selector)">
                    </div>

                    <div class="col-12 mt-3 d-grid">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-floppy"></i> Save
                        </button>
                    </div>
                </form>
            </div>

            <div class="col-12 col-lg-9">
                <feed-selector-iframe
                    :url="feedUrl"
                    :parent-selector="activeSelectorParentValue"
                    :value="activeSelectorValue"
                    @input="setSelectorValue">
                </feed-selector-iframe>
            </div>
        </div>
    `,
    computed: {
        activeSelectorValue() {
            if (this.activeSelector != null) {
                if (this.activeSelector.value) {
                    return this.activeSelector.value
                } else {
                    return ""
                }
            } else {
                return null
            }
        },

        activeSelectorParentValue() {
            if (this.activeSelector != null && this.activeSelector["parent"]) {
                let parent = this.selectors[this.activeSelector["parent"]]
                return parent.value
            } else {
                return null
            }
        },
    },
    methods: {
        select(selector) {
            if (this.activeSelector) {
                this.unselect(this.activeSelector)
            }

            this.activeSelector = selector
        },

        unselect(selector) {
            this.activeSelector = null
        },

        setSelectorValue(value) {
            if (this.activeSelector != null) {
                this.activeSelector.value = value
            }
        },
    },
}

app.component("feed-selector-form", FeedSelectorForm)

let FeedSelectorIframe = {
    props: {
        url: { type: String, required: true },
        parentSelector: { type: String, required: false },
        value: { type: String, required: false },
    },
    emits: ["input"],
    data() {
        return {
            highlightElements: [],
            parentElements: new Set(),

            // Required to restore the initial value if the user move out of the iframe without
            // selecting an element.
            savedValue: null,
        }
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
                v-if="value == null"
                style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    height: 100%;
                    width: 100%;
                    border-radius: var(--bs-border-radius);

                    z-index: 1000;

                    background-color: rgba(0, 0, 0, 0.25);
                    backdrop-filter: blur(6px);

                    color: white;
                    text-shadow: 0 0 1px rgba(0, 0, 0, 1);
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
                    <span class="d-none d-lg-inline">← </span>Pick a content selector first
                </p>
            </div>

            <iframe
                ref="frame"
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
    mounted() {
        this.$refs["frame"].onload = this.onLoad
    },
    watch: {
        value() {
            this.highlightCurrentValue()
        },
        parentSelector() {
            this.setParentElements()
        },
    },
    methods: {
        onLoad() {
            this.highlightCurrentValue()

            let body = this.$refs["frame"].contentDocument.querySelector("body")
            body.style.cursor = "pointer"

            body.onmousemove = this.onMouseMove
            body.onmouseout = this.onMouseOut
            body.onclick = this.onClick

            this.setParentElements()
        },

        onMouseMove(event) {
            // Highlights the element underneath the mouse cursor, and the items sharing the same
            // selector.

            var isInsideParent = false
            for (parent of this.parentElements) {
                if (parent.contains(event.target)) {
                    isInsideParent = true
                    break
                }
            }

            if (!isInsideParent) {
                this.onMouseOut()
                return
            }

            let selector = this.getElementSelector(event.target)

            if (selector) {
                if (!this.savedValue) {
                    this.savedValue = this.value
                }

                this.$emit("input", selector)

                this.highlightCurrentValue()
            }
        },

        onMouseOut(event) {
            // Cancels visually selection of elements, and resets the initial value.

            if (this.savedValue != null) {
                this.$emit("input", this.savedValue)
            }

            this.savedValue = null

            this.highlightCurrentValue()
        },

        onClick(event) {
            this.savedValue = null

            return false // Prevents default action
        },

        highlightCurrentValue() {
            if (!this.value) {
                return
            }

            var selector;
            if (this.parentSelector) {
                selector = this.parentSelector + " " + this.value
            } else {
                selector = this.value
            }

            this.highlightSelector(selector)
        },

        highlightSelector(selector)
        {
            this.removeHighlights()

            if (!selector) {
                return
            }

            let frame = this.$refs["frame"]

            let elements = frame.contentDocument.querySelectorAll(selector)

            for (let element of elements) {
                this.addHighlight(element)
            }
        },

        removeHighlights() {
            for (let element of this.highlightElements) {
                element.remove()
            }

            this.highlightElements = []
        },

        addHighlight(element) {
            // Displays a box around the provided element.

            let frame = this.$refs["frame"]

            let rect = element.getBoundingClientRect()
            let x = rect.left + frame.contentWindow.window.scrollX
            let y = rect.top + frame.contentWindow.window.scrollY

            highlightElement = frame.contentDocument.createElement("div")
            frame.contentDocument.body.appendChild(highlightElement);

            let style = highlightElement.style

            style.pointerEvents = "none" // Prevents onmousemove events for this element.

            style.position = "absolute"
            style.left = x + "px"
            style.top = y + "px"
            style.width = rect.width + "px"
            style.height = rect.height + "px"

            style.border = "0.25rem solid rgba(13, 110, 253, 0.5)"
            style.borderRadius = "0.25rem"

            this.highlightElements.push(highlightElement)
        },

        getElementSelector(element) {
            // Returns a DOM selector from the DOM element.

            var selector = ""

            while (element && element.tagName && !this.parentElements.has(element)) {
                currentSelector = element.tagName.toLowerCase()

                for (className of element.classList) {
                    currentSelector += "." + className
                }

                if (selector) {
                    selector = currentSelector + " " + selector
                } else {
                    selector = currentSelector
                }

                element = element.parentElement
            }

            return selector;
        },

        setParentElements() {
            // Sets the `parentElements` field with the elements matching `parentSelector`.

            let body = this.$refs["frame"].contentDocument.querySelector("body")

            if (this.parentSelector) {
                this.parentElements = new Set(body.querySelectorAll(this.parentSelector))
            } else {
                // When no parent selector is set, the parent element is `<body>`.
                this.parentElements = new Set([body])
            }
        },
    },
}

app.component("feed-selector-iframe", FeedSelectorIframe)

app.mount('#app')
