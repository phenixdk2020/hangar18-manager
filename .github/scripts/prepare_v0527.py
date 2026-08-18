from pathlib import Path
p=Path('.github/scripts/patch_v0527.py')
t=p.read_text()
old="""    $pageDataContextTypeV0524.on('change', function () { refreshPageDataContextEntriesV0524(false); refreshDynamicBindingsV0524($('.h18-pages-admin')); refreshAllCanvasPreviews(); });
    $pageDataContextEntryV0524.on('change', function () { $(this).attr('data-current-entry', String($(this).val() || '0')); refreshAllCanvasPreviews(); });
"""
actual="""    $pageDataContextTypeV0524.on('change', function () { refreshPageDataContextEntriesV0524(false); refreshDynamicBindingsV0524($pageSections); refreshAllCanvasPreviews(); scheduleEditorHistoryCapture(0); });
    $pageDataContextEntryV0524.on('change', function () { $(this).attr('data-current-entry', String($(this).val() || 0)); refreshAllCanvasPreviews(); scheduleEditorHistoryCapture(0); });
"""
old_new="""    $pageDataContextTypeV0524.on('change', function () { refreshPageDataContextEntriesV0524(false); refreshDynamicBindingsV0524($('.h18-pages-admin')); refreshAllCanvasPreviews(); $pageSections.children('.h18-page-section-row').each(function(){evaluateConditionPreviewV0527($(this));}); });
    $pageDataContextEntryV0524.on('change', function () { $(this).attr('data-current-entry', String($(this).val() || '0')); refreshAllCanvasPreviews(); $pageSections.children('.h18-page-section-row').each(function(){evaluateConditionPreviewV0527($(this));}); });
"""
actual_new="""    $pageDataContextTypeV0524.on('change', function () { refreshPageDataContextEntriesV0524(false); refreshDynamicBindingsV0524($pageSections); refreshAllCanvasPreviews(); $pageSections.children('.h18-page-section-row').each(function(){evaluateConditionPreviewV0527($(this));}); scheduleEditorHistoryCapture(0); });
    $pageDataContextEntryV0524.on('change', function () { $(this).attr('data-current-entry', String($(this).val() || 0)); refreshAllCanvasPreviews(); $pageSections.children('.h18-page-section-row').each(function(){evaluateConditionPreviewV0527($(this));}); scheduleEditorHistoryCapture(0); });
"""
if old not in t or old_new not in t:
    raise SystemExit('v0.5.27 patch definition context anchor missing')
t=t.replace(old,actual,1).replace(old_new,actual_new,1)
p.write_text(t)
print('v0.5.27 data-context preview anchor prepared')
